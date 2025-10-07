import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
        connect_args={"check_same_thread": False}
    )
    
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def test_db(engine):
    """Creates an isolated DB session for each test. 
    
    Transactions are rolled back at the end (quick cleanup).
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
        transaction.rollback()
        connection.close()
        
