from fastapi import APIRouter, status

from todo_api.dependencies import db_dependency, user_dependency
from todo_api.models import User
from todo_api.schema import Message, UpdateUserRequest, UpdatePasswordRequest, UserOutput

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