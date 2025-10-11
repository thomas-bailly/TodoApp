from fastapi import APIRouter, status, Query

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

# ================================ Get Todos ================================= #
@router.get("", status_code=status.HTTP_200_OK, response_model=list[TodoOutput])
async def read_all_todos(db: db_dependency, user: user_dependency,
                         complete: bool | None = Query(default=None)) -> list[TodoOutput]:
    
    # Base query filtering todos by the authenticated user
    query = db.query(Todo).filter(Todo.owner_id == user.id)
    
    # If 'complete' is provided, further filter the todos
    if complete is not None:
        query = query.filter(Todo.complete == complete)
    
    # query execution and return results: a list of TodoOutput
    return query.all()