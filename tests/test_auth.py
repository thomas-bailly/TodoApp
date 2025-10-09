import pytest
import pytest_asyncio
from fastapi import status, HTTPException
from jose import jwt
from datetime import datetime, timedelta, timezone

from todo_api.config import settings
from todo_api.models import User
from todo_api.security import credential_exception
from todo_api.dependencies import get_current_user
from todo_api.routers.auth import authenticate_user
from tests.utils import model_to_dict


class TestRegister:
    
    def test_register_user_sucess(self, client, db):
        
        user_data = {
            "username":"NewUser",
            "email":"new@mail.com",
            "role":"user",
            "password":"PassWord"
        }
        
        # Send POST request to create the user
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "User created successfully."
        
        db.expire_all()
        
        # Verify that the user is in the database
        user_in_db = db.query(User).filter(
            User.username == user_data["username"]
        ).first()
        
        assert user_in_db is not None
        
        user_data_db = model_to_dict(user_in_db, exclude={"id",
                                                          "hashed_password",
                                                          "is_active"})
        for field, value in user_data_db.items():
            assert value == user_data.get(field)
            
class TestLogin:

    def test_authenticate_user_success(self, client, db, test_user):
        
        auth_user = authenticate_user(username=test_user.username,
                                      password="testpassword",
                                      db=db)
        
        assert auth_user
        
        for field, value in model_to_dict(auth_user).items():
            assert value == getattr(test_user, field)
            
    def test_authenticate_user_wrong_password(self, client, db, test_user):
        
        auth_user = authenticate_user(username=test_user.username,
                                      password="anypassword",
                                      db=db)
        assert auth_user is None
        
    def test_authenticate_user_unknow_user(self, client, db, test_user):
        
        auth_user = authenticate_user(username="AnyUser",
                                      password="testpassword",
                                      db=db)
        assert auth_user is None
        
    def test_login_success(self, client, db, test_user):
        
        login_data = {
            "username": test_user.username,
            "password": "testpassword"
        }
        
        # Send POST request to login, form data so we use 'data' not 'json'
        response = client.post("/auth/token", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        
        token_response = response.json()
        assert "access_token" in token_response
        assert isinstance(token_response["access_token"], str)
        assert len(token_response["access_token"]) > 0
        assert token_response["token_type"] == "bearer"
        
    def test_login_unhauthorized(self, client, db, test_user):
        
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }
        
        # Send POST request to login, form data so we use 'data' not 'json'
        response = client.post("/auth/token", data=login_data)
        assert response.status_code == credential_exception.status_code
        assert response.json()["detail"] == credential_exception.detail


class TestCurrentUser:
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, client, db, test_user):
        
        to_encode = {
            "sub": test_user.username,
            "id": test_user.id,
            "role": test_user.role
        }
        
        token = jwt.encode(
            claims=to_encode,
            key=settings.secret_key,
            algorithm=settings.algorithm
        )
        
        user = await get_current_user(token=token, db=db)
        
        for field, value in model_to_dict(user).items():
            assert value == getattr(test_user, field)
            
    @pytest.mark.asyncio
    async def test_get_current_user_missing_value(self, client, db, test_user):
        
        to_encode = {
            "sub": test_user.username
        }
        
        token = jwt.encode(
            claims=to_encode,
            key=settings.secret_key,
            algorithm=settings.algorithm
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db)
        
        assert exc_info.value.status_code == credential_exception.status_code
        assert exc_info.value.detail == credential_exception.detail
        
    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, client, db, test_user):
        
        to_encode = {
            "sub": test_user.username,
            "id": test_user.id,
            "role": test_user.role,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5)
        }
        
        token = jwt.encode(
            claims=to_encode,
            key=settings.secret_key,
            algorithm=settings.algorithm
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db)
        
        assert exc_info.value.status_code == credential_exception.status_code
        assert exc_info.value.detail == credential_exception.detail
        
    @pytest.mark.asyncio
    async def test_get_current_user_deleted_user(self, client, db, test_user):
        
        to_encode = {
            "sub": test_user.username,
            "id": test_user.id,
            "role": test_user.role
        }
        
        token = jwt.encode(
            claims=to_encode,
            key=settings.secret_key,
            algorithm=settings.algorithm
        )
        
        db.delete(test_user)
        db.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db)
        
        assert exc_info.value.status_code == credential_exception.status_code
        assert exc_info.value.detail == credential_exception.detail