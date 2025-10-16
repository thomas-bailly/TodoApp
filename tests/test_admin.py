from fastapi import status

from todo_api.models import Todo, User

class TestReadUser:
    
    def test_read_all_users(db, admin_client, test_admin, test_user):
        
        # Send GET request
        response = admin_client.get("/admin/users")
        assert response.status_code == status.HTTP_200_OK
        
        user_list = response.json()
        assert len(user_list) == 2
        
    def test_read_all_users_non_admin(db, auth_client, test_user):
        
        # Send GET request
        response = auth_client.get("/admin/users")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Operation requires administrator privileges."