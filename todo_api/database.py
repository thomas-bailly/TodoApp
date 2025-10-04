from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={'check_same_thread': False},
                       future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models, all model classes should inherit from this.
Base = declarative_base()

def get_db():
    """
    Provide a SQLAlchemy database session for FastAPI dependencies.

    This generator creates a new database session, yields it to the calling
    endpoint (or background task), and ensures that the session is properly
    closed after use, even if an exception occurs.

    Yields:
        Session: An active SQLAlchemy session connected to the database.

    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

