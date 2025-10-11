from fastapi import APIRouter, status

from todo_api.dependencies import db_dependency, user_dependency
from todo_api.schema import Message, TodoRequest, TodoUpdateRequest, TodoOutput
from todo_api.models import Todo

router = APIRouter(prefix="/todos", tags=["todos"])

# =============================== Create Todos =============================== #
@router.post("", status_code=status.HTTP_201_CREATED, response_model=Message)
async def create_todo(todo_request: TodoRequest, db: db_dependency,
                      user: user_dependency) -> Message:
    
    new_todo = Todo(**todo_request.model_dump(), owner_id=user.id)
    db.add(new_todo)
    db.commit()
    
    return Message(message="Todo created successfully.")