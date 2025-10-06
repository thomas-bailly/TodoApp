from fastapi import APIRouter, status, HTTPException, Path
from todo_api.dependencies import db_dependency
from todo_api.models import User
from todo_api.schema import CreateUserRequest, Message, Token
from todo_api.security import hash_password, verify_password, create_access_token


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