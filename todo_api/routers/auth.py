from fastapi import APIRouter, status, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta

from todo_api.dependencies import db_dependency
from todo_api.models import User
from todo_api.schema import CreateUserRequest, Message, TokenOutput
from todo_api.security import hash_password, verify_password, create_access_token, credential_exception
from todo_api.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])

# ============================= Create a new user ============================ #
@router.post("/register", status_code=status.HTTP_201_CREATED,
             description="Register a new user account with username, email and password",
             response_model=Message)
async def register_user(user_request: CreateUserRequest, db: db_dependency) -> Message:
    """Handles user registration.
    
    Hashes the password and creates a new user entry in the database if the 
    username and email are unique.
    """
    
    user_dict = user_request.model_dump()
    
    # Hash the password
    user_dict["hashed_password"] = hash_password(user_dict.pop("password"))
    
    # Create a new user
    new_user = User(**user_dict)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return Message(message="User created successfully.")

# ====================== Access and User Authentication ====================== #
def authenticate_user(username: str, password: str, db: db_dependency) -> User | None:
    """Authenticate a user by username and password.

    Args:
        username (str): The username.
        password (str): The password of the user.
        db (db_dependency): Database session.

    Returns:
        User: The authenticated user object if credentials are valid, else False.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    if verify_password(password=password, hashed_password=user.hashed_password):
        return user
    else:
        return None
    
@router.post("/token", response_model=TokenOutput, status_code=status.HTTP_200_OK,
             description="Authenticates the user using username and password"
             " (form data) and returns a JWT access token.")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency) -> TokenOutput:
    """Handles user login by authenticating credentials and issuing a JWT access token.

    Raises:
        HTTPException (401 UNAUTHORIZED): If the provided username or password
        is incorrect.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise credential_exception
        
    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expire_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return TokenOutput(access_token=token, token_type="bearer")