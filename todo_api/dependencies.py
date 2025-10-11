from fastapi import Depends, Path, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Annotated
from todo_api.database import SessionLocal
from todo_api.config import settings
from todo_api.security import decode_access_token, credential_exception
from todo_api.models import User, Todo


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

# ========================= Get Todo By Id Dependency ======================== #
def get_todo_by_id(db: db_dependency, user: user_dependency,
                   todo_id: int = Path(gt=0)) -> Todo:
    """Retrieve a Todo item by its ID, ensuring it belongs to the authenticated user.
    
    Args:
        db (Session): The database session dependency.
        user (User): The authenticated User object.
        todo_id (int): The ID of the Todo item to retrieve.
    
    Returns:
        Todo: The requested Todo item.
        
    Raises:
        HTTPException (404 NOT FOUND): If the Todo item does not exist or is not
    """
    
    
    # Query to find the todo by ID and ensure it belongs to the authenticated user
    todo = db.query(Todo).filter(Todo.owner_id == user.id,
                                 Todo.id == todo_id).first()
    
    # If no todo is found, raise a 404 error
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or not owned by the user."
        )
    
    return todo

get_todo_dependency = Annotated[Todo, Depends(get_todo_by_id)]