import re
from fastapi import status

from todo_api.models import Todo
from tests.utils import model_to_dict


class TestCreateTodo:
    
    def test_create_todo_success(self, auth_client, db, test_user):
        
        todo_data = {
            "title": "Test todo",
            "description": "A test todo.",
            "priority": 3
        }
        
        # Send POST request
        response = auth_client.post("/todos", json=todo_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "Todo created successfully."
        
        # Ensure the session is up-to-date
        db.expire_all()
        
        # Verify that the todo is in the database
        todo = db.query(Todo).filter(Todo.owner_id == test_user.id).first()
        assert todo is not None
        # Default values
        assert todo.complete is False
        
        # Verify the fields
        for field, value in model_to_dict(todo, exclude={"complete",
                                                         "owner_id",
                                                         "id"}).items():
            assert value == todo_data[field]
            
class TestReadAllTodos:
    
    def test_read_all_todos(self, auth_client, test_todos, test_user):
        
        # Send GET request
        response = auth_client.get("/todos")
        assert response.status_code == status.HTTP_200_OK
        
        todos_list = response.json()
        assert len(todos_list) == 2
        
        returned_owner_id = {todo["owner_id"] for todo in todos_list}
        expected_owner_id = {test_user.id}
        assert returned_owner_id == expected_owner_id
        
    def test_read_all_todos_completed(self, auth_client, test_todos, test_user):
        
        # Send GET request
        response = auth_client.get("/todos?complete=true")
        assert response.status_code == status.HTTP_200_OK
        
        todo_list = response.json()
        assert len(todo_list) == 1
        
        for todo in todo_list:
            assert todo["complete"] is True
            assert todo["owner_id"] == test_user.id
        
    def test_read_all_todos_search(self, auth_client, test_todos, test_user):
        
        # Send GET request
        response = auth_client.get("/todos?search=complete")
        assert response.status_code == status.HTTP_200_OK
        
        todo_list = response.json()
        assert len(todo_list) == 1
        
        pattern = re.compile('complete', re.IGNORECASE)
        
        for todo in todo_list:
            assert (pattern.search(todo["title"]) or pattern.search(todo["description"]))
            assert todo["owner_id"] == test_user.id

class TestReadTodo:
    
    def test_read_todo_success(self, auth_client, test_todos, test_user):
        
        # Get a reference to a todo owned by test_user
        todo_ref = test_todos["user"][0]
        
        # Send GET request
        response = auth_client.get(f"/todos/{todo_ref.id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the returned todo data
        todo = response.json()
        
        for field, value in todo.items():
            assert value == getattr(todo_ref, field)
            
        assert todo["owner_id"] == todo_ref.owner_id
        
    def test_read_todo_not_found(self, auth_client, test_todos, test_user):
        
        # Send GET request
        response = auth_client.get("/todos/42")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todo not found or not owned by the user."
        
    def test_read_todo_not_owned(self, auth_client, test_todos, test_user):
        
        # Get a reference to a todo owned by test_admin
        todo_ref = test_todos["admin"][0]
        
        # Send GET request
        response = auth_client.get(f"/todos/{todo_ref.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todo not found or not owned by the user."
        
class TestUpdateTodo:
    
    def test_update_todo_success(self, auth_client, db, test_todos, test_user):
        
        # Get a reference to a todo owned by test_user
        todo_ref = test_todos["user"][0]
        
        updated_data = {
            "title": "Updated Todo",
            "complete": True
        }
        
        old_data = {f:v for f, v in model_to_dict(todo_ref).items()
                    if f not in updated_data}
        
        # Send PUT request
        response = auth_client.put(f"/todos/{todo_ref.id}", json=updated_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Todo updated successfully."
        
        db.refresh(todo_ref)
        
        # Verify updated fields
        for field, value in updated_data.items():
            assert value == getattr(todo_ref, field)
            
        # Verify unchanged fields
        for field, value in old_data.items():
            assert value == getattr(todo_ref, field)
            
    def test_update_todo_non_updatable_field(self, auth_client, db,
                                             test_todos, test_user):
        
        # Get a reference to a todo owned by test_user
        todo_ref = test_todos["user"][0]
        
        updated_data = {
            "owner_id": 2
        }
        
        # Send PUT request
        response = auth_client.put(f"/todos/{todo_ref.id}", json=updated_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        
        db.refresh(todo_ref)
        
        # Verify updated fields
        for field, value in updated_data.items():
            assert value != getattr(todo_ref, field)
        