from fastapi import APIRouter, status, HTTPException, Query, Path
from sqlalchemy import or_

from todo_api.dependencies import db_dependency, user_dependency, get_todo_dependency
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
                         complete: bool | None = Query(default=None),
                         search: str | None = Query(default=None)) -> list[TodoOutput]:
    
    # Base query filtering todos by the authenticated user
    query = db.query(Todo).filter(Todo.owner_id == user.id)
    
    # If 'complete' is provided, further filter the todos
    if complete is not None:
        query = query.filter(Todo.complete == complete)
        
    if search is not None:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Todo.title.ilike(pattern),
                Todo.description.ilike(pattern)
            )
        )
    
    # query execution and return results: a list of TodoOutput
    return query.all()

@router.get("/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoOutput)
async def read_todo(db: db_dependency, user: user_dependency,
                    todo: get_todo_dependency) -> TodoOutput:
    
    return todo

# =============================== Update Todos =============================== #
@router.put("/{todo_id}", status_code=status.HTTP_200_OK, response_model=Message)
async def update_todo(todo_request: TodoUpdateRequest, db: db_dependency,
                      user: user_dependency, todo: get_todo_dependency) -> Message:
     
    # for loop to update attributes
    for field, value in todo_request.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
        
    db.commit()
    return Message(message="Todo updated successfully.")

# =============================== Delete Todos =============================== #
@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, user: user_dependency,
                      todo: get_todo_dependency):
    
    db.delete(todo)
    db.commit()
    return