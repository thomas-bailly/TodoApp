from fastapi import APIRouter, status, HTTPException

from todo_api.dependencies import db_dependency, user_dependency
from todo_api.models import User
from todo_api.schema import Message, UpdateUserRequest, UpdatePasswordRequest, UserOutput
from todo_api.security import hash_password, verify_password, credential_exception


router = APIRouter(prefix='/user', tags=["user"])

# ================================= Get User ================================= #
@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserOutput)
async def read_user_me(user: user_dependency, db: db_dependency) -> UserOutput:
    return UserOutput.model_validate(user)

# =============================== Update User ================================ #
@router.put("/me", status_code=status.HTTP_200_OK, response_model=Message)
async def update_user_me(update_request: UpdateUserRequest, user: user_dependency,
                         db: db_dependency) -> Message:
    
    # for loop to update attributes
    for field, value in update_request.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
            
    db.commit()
    return Message(message="User updated successfully.")

# ============================ Change Password =============================== #
@router.put("/me/password", status_code=status.HTTP_200_OK, response_model=Message)
async def change_password(password_request:UpdatePasswordRequest, user:user_dependency,
                          db:db_dependency) -> Message:
    
    # Veridy if the old and new password are identical
    if password_request.old_password == password_request.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The new password must be different from the current password."
        )

    # Verify the old password
    if not verify_password(password=password_request.old_password, 
                           hashed_password=user.hashed_password):
        
        raise credential_exception
    
    # Update password
    user.hashed_password = hash_password(password_request.new_password)
    
    db.commit()
    return Message(message="Password updated successfully.")