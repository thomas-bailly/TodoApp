from fastapi import APIRouter, status, HTTPException, Query, Path

from todo_api.dependencies import db_dependency, admin_dependency
from todo_api.schema import Message, UserOutput, TodoOutput, AdminUpdateUserRequest
from todo_api.models import User, Todo

router = APIRouter(prefix="/admin", tags=["admin"])

# ================================= Get User ================================= #
@router.get("/users", status_code=status.HTTP_200_OK, response_model=list[UserOutput])
async def read_all_users(db: db_dependency, admin: admin_dependency,
                         role: str | None = Query(default=None),
                         username: str | None = Query(default=None)) -> list[UserOutput]:
    
    # Base query filtering
    query = db.query(User)
    
    # If 'role' is provided, further filter the users
    if role is not None:
        query = query.filter(User.role == role)
    
    # If 'username' is provided, further filter the users
    if username is not None:
        query = query.filter(User.username.ilike(f"{username}%"))
        
    return query.all()

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=UserOutput)
async def read_user(db: db_dependency, admin: admin_dependency,
                    user_id: int = Path(gt=0)) -> UserOutput:
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return user

# ================================= Get Todo ================================= #
@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoOutput)
async def read_todo(db: db_dependency, admin: admin_dependency,
                    todo_id: int = Path(gt=0)) -> TodoOutput:
    
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found."
        )
    
    return todo

@router.get("/users/{user_id}/todos", status_code=status.HTTP_200_OK, response_model=list[TodoOutput])
async def read_user_todos(db: db_dependency, admin: admin_dependency,
                          user_id: int = Path(gt=0)) -> list[TodoOutput]:
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return db.query(Todo).filter(Todo.owner_id == user.id).all()

# =============================== Update User =============================== #
@router.put("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=Message)
async def update_user(update_request: AdminUpdateUserRequest, db: db_dependency,
                      admin: admin_dependency, user_id: int = Path(gt=0)) -> Message:
    
    user = db.query(User).filter(User.id == user_id).first()
    
    # for loop to update attributes
    for field, value in update_request.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
            
    db.commit()
    return Message(message="User updated successfully.")