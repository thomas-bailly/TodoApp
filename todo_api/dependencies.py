from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from todo_api.database import SessionLocal


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
        
# ============================== DB Dependency =============================== #
db_dependency = Annotated[Session, Depends(get_db)]