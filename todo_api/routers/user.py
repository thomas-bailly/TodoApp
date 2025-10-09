from fastapi import APIRouter, status

from todo_api.dependencies import db_dependency, user_dependency
from todo_api.models import User
from todo_api.schema import Message, UpdateUserRequest, UpdatePasswordRequest, UserOutput


router = APIRouter(prefix='/user', tags=["user"])

# ================================= Get User ================================= #
@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserOutput)
async def read_user_me(user: user_dependency, db: db_dependency) -> UserOutput:
    return UserOutput.model_validate(user)