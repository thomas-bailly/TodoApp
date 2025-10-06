from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Annotated
from todo_api.database import SessionLocal
from todo_api.config import settings
from todo_api.security import decode_access_token, credential_exception
from todo_api.models import User


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

# ========================= Current User Dependency ========================== #
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)],
                           db: db_dependency) -> User:
    """Retrieve the current User object from a valid JWT token.
    
    Args:
        token (str): The JWT token extracted from the Authorization header.
        db (Session): The database session dependency.
        
    Returns:
        User: The authenticated SQLAlchemy User object.
    
    Raises:
        HTTPException (401 UNAUTHORIZED): If the token is invalid or the user is
        not found.
    """
    
    token_data = decode_access_token(token)
    
    user = db.query(User).filter(
        User.id == token_data["id"]
    ).first()
    
    if user is None:
        raise credential_exception
    
    return user

user_dependency = Annotated[User, Depends(get_current_user)]