from fastapi import status

from tests.utils import model_to_dict
from todo_api.security import verify_password
from todo_api.models import Todo, User

class TestReadUser:
    
    def test_read_user_me(self, auth_client, db, test_user):
        
        # Send GET request
        response = auth_client.get("/user/me")
        assert response.status_code == status.HTTP_200_OK
        
        user_data = response.json()
        for field, value in user_data.items():
            assert value == getattr(test_user, field)

class TestUpdateUser:
    
    def test_update_user_me_success(self, auth_client, db, test_user):
        
        new_data = {
            "first_name": "Alice",
            "email": "alice@email.com"
        }
        
        old_data = {f:v for f, v in model_to_dict(test_user).items() if f not in new_data}
        
        # Send PUT request
        response = auth_client.put("/user/me", json=new_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "User updated successfully."
        
        db.refresh(test_user)
        
        # Verify updated fields
        for field, value in new_data.items():
            assert value == getattr(test_user, field)
            
        # Verify unchanged fields
        for field, value in old_data.items():
            assert value == getattr(test_user, field)
            
    def test_update_user_me_duplicate_username(self, auth_client, db, test_user, test_admin):
        
        new_data = {
            "username":"TestAdmin"
        }
        
        # Send PUT request
        response = auth_client.put("/user/me", json=new_data)
        
        # Verify the status code and detail
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Username already exists."
        
    def test_update_user_me_duplicate_email(self, auth_client, db, test_user, test_admin):
        
        new_data = {
            "email":"admin@email.com"
        }
        
        # Send PUT request
        response = auth_client.put("/user/me", json=new_data)
        
        # Verify the status code and detail
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Email already exists."

class TestChangePassword:
    
    def test_change_password_success(self, auth_client, db, test_user):
        
        password_data = {
            "old_password":"testpassword",
            "new_password":"newpassword"
        }
        
        old_hashed = test_user.hashed_password
        
        # Send PUT request
        response = auth_client.put("/user/me/password", json=password_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password updated successfully."
        
        db.refresh(test_user)
        
        # Verify that the password has changed
        assert test_user.hashed_password != old_hashed
        assert verify_password(password_data["new_password"], test_user.hashed_password)
        
    def test_change_password_wrong_old_password(self, auth_client, db, test_user):
        
        password_data = {
            "old_password":"wrongpassword",
            "new_password":"newpassword"
        }
        
        old_hashed = test_user.hashed_password
        
        # Send PUT request
        response = auth_client.put("/user/me/password", json=password_data)
        
        # Verify the status code and detail
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate user."
        
        db.refresh(test_user)
        
        # Verify that the password has not changed
        assert test_user.hashed_password == old_hashed
        assert verify_password("testpassword", test_user.hashed_password)
        
    def test_change_password_same_as_old(self, auth_client, db, test_user):
        
        password_data = {
            "old_password":"testpassword",
            "new_password":"testpassword"
        }
        
        old_hashed = test_user.hashed_password
        
        # Send PUT request
        response = auth_client.put("/user/me/password", json=password_data)
        
        # Verify the status code and detail
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "The new password must be different from the current password."
        
        db.refresh(test_user)
        
        # Verify that the password has not changed
        assert test_user.hashed_password == old_hashed
        assert verify_password("testpassword", test_user.hashed_password)
        
class TestDeleteUser:
    
    def test_delete_user_me(self, auth_client, db, test_user):
        
        user_id = test_user.id
        
        # Create a todo for the user
        todo = Todo(
            title="Sample Todo",
            description="A sample todo item.",
            owner_id=user_id
        )
        
        db.add(todo)
        db.commit()
        db.refresh(todo)
        
        # Verify the todo exists
        todo_in_db = db.query(Todo).filter(Todo.id == todo.id).first()
        assert todo_in_db is not None
        
        todo_id = todo.id
        
        # Send DELETE request
        response = auth_client.delete("/user/me")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the user is deleted
        user_in_db = db.query(User).filter(User.id == user_id).first()
        assert user_in_db is None
        
        # Verify the user's todos are deleted
        todo_in_db = db.query(Todo).filter(Todo.id == todo_id).first()
        assert todo_in_db is None