from fastapi import status

from todo_api.models import Todo, User

class TestReaAllUser:
    
    def test_read_all_users(db, admin_client, test_admin, test_user):
        
        # Send GET request
        response = admin_client.get("/admin/users")
        assert response.status_code == status.HTTP_200_OK
        
        user_list = response.json()
        assert len(user_list) == 2
        
    def test_read_all_users_role_filter(db, admin_client, test_admin, test_user):
        
        # Send GET request
        response = admin_client.get("/admin/users?role=user")
        assert response.status_code == status.HTTP_200_OK
        
        user_list = response.json()
        assert len(user_list) == 1
        
        assert user_list[0]["role"] == "user"
        
    def test_read_all_users_username_filter(db, admin_client, test_admin, test_user):
        
        pattern = "TestU"
        
        # Send GET request
        response = admin_client.get(f"/admin/users?username={pattern}")
        assert response.status_code == status.HTTP_200_OK
        
        user_list = response.json()
        assert len(user_list) == 1
        
        assert user_list[0]["username"].startswith(pattern)
        
    def test_read_all_users_is_active_filter(db, admin_client, test_admin,
                                             test_inactive_user):
        
        # Send GET request
        response = admin_client.get("/admin/users?is_active=False")
        assert response.status_code == status.HTTP_200_OK
        
        user_list = response.json()
        assert len(user_list) == 1
        
        assert user_list[0]["is_active"] is False

class TestReadUser:
    
    def test_read_user(db, admin_client, test_admin, test_user):
        
        # Send GET request
        response = admin_client.get(f"/admin/users/{test_user.id}")
        assert response.status_code == status.HTTP_200_OK
        
        user_data = response.json()
        for field, value in user_data.items():
            assert value == getattr(test_user, field)
            
    def test_read_user_not_found(db, admin_client, test_admin, test_user):
        
        # Send GET request
        response = admin_client.get("/admin/users/42")
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestReadTodo:
    
    def test_read_todo(db, admin_client, test_admin, test_todos):
        
        todo_ref = test_todos["user"][0]
        
        # Send GET request
        response = admin_client.get(f"/admin/todos/{todo_ref.id}")
        assert response.status_code == status.HTTP_200_OK
        
        todo = response.json()
        
        for field, value in todo.items():
            assert value == getattr(todo_ref, field)

    def test_read_todo_not_found(db, admin_client, test_admin, test_todos):
        
        # Send GET request
        response = admin_client.get("/admin/todos/42")
        assert response.status_code == status. HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todo not found."
        

class TestNonAdminUser:
    
    def test_read_all_users(db, auth_client, test_user):
        
        # Send GET request
        response = auth_client.get("/admin/users")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Operation requires administrator privileges."
        
    def test_read_user(db, auth_client, test_user):
        
        # Send GET request
        response = auth_client.get(f"/admin/users/{test_user.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Operation requires administrator privileges."
        
    def test_read_todo(db, auth_client, test_user, test_todos):
        
        todo_id = test_todos["user"][0].id
        
        # Send GET request
        response = auth_client.get(f"/admin/todos/{todo_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Operation requires administrator privileges."
        
    def test_read_user_todos(db, auth_client, test_user, test_todos):
        
        # Send GET request
        response = auth_client.get(f"/admin/users/{test_user.id}/todos")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Operation requires administrator privileges."
        
    def test_update_user(db, auth_client, test_user):
        
        new_data = {
            "first_name": "Updated Name"
        }
        
        # Send PUT request
        response =  auth_client.put(f"/admin/users/{test_user.id}", json=new_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Operation requires administrator privileges."
        
    def test_delete_user(db, auth_client, test_user, test_inactive_user):
        
        inactive_id = test_inactive_user.id
        
        # Send DELETE request
        response = auth_client.delete(f"/admin/users/{inactive_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Operation requires administrator privileges."