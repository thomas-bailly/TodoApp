import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from todo_api.database import Base
from todo_api.api import app
from todo_api.dependencies import get_db
from todo_api.models import User
from todo_api.security import hash_password

# ============================= DB Setup Fixtures ============================ #
@pytest.fixture(scope="session")
def engine():
    """Creates the SQLAlchemy engine for an in-memory SQLite database."""
    
    # StaticPool ensures that the same thread is always used for SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool=StaticPool
    )
    
    Base.metadata.create_all(bind=engine)
    yield engine

def get_transactional_session(engine):
    """Creates an isolated DB session for each test.

    Transactions are rolled back at the end (quick cleanup).
    
    Args:
        engine: The SQLAlchemy engine instance provided by the engine fixture.

    Yields:
        db: A SQLAlchemy session object scoped to the test function.
    """
    
    connection = engine.connect()
    transaction = connection.begin()
    
    # Local session for this connection and transaction
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        # Cancels the transaction to delete all data created by the test
        db.close()
        transaction.rollback()
        connection.close()
        
@pytest.fixture(scope="function")
def db(engine):
    """Fixture to provide a SQLAlchemy session for a test function."""
    yield from get_transactional_session(engine)

def override_get_db(engine):
    """Dependency override to use the test database session."""
    def _override_get_db():
        yield from get_transactional_session(engine)
    return _override_get_db

# ========================== Test Client Fixture ============================= #
@pytest.fixture(scope="function")
def client(engine):
    """Fixture to provide a FastAPI TestClient with overridden dependencies."""
    
    # Override the get_db dependency to use the test database session
    app.dependency_overrides[get_db] = override_get_db(engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up overrides after the test
    app.dependency_overrides.clear()
    
# ============================ User Fixture ================================== #
@pytest.fixture(scope="function")
def test_user(db):
    """Fixture to create a test user in the database."""
    
    user = User(
        username="TestUser",
        email="test-user@email.com",
        first_name="Test",
        last_name="User",
        role="admin",
        phone_number="+33612345678",
        hashed_password=hash_password("testpassword")
    )
    
    db.add(user)
    db.flush()
    db.refresh(user)
    yield user