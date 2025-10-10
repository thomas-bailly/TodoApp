from fastapi import status

from tests.utils import model_to_dict
from todo_api.security import verify_password

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