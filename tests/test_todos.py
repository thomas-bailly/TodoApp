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