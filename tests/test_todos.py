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