from todo_api.security import hash_password, verify_password, create_access_token, decode_access_token, credential_exception
from todo_api.config import settings
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
import pytest

def test_hash_password():
    password = 'strongpassword'
    hashed_password = hash_password(password)
    
    assert hashed_password != password
    assert hashed_password.startswith("$argon2id$")
    assert len(hashed_password) > 50

def test_verify_password():
    password = 'strongpassword'
    hashed_password = hash_password(password)
    
    # Success
    assert verify_password(password=password,
                           hashed_password=hashed_password) is True
    
    # Mismatch
    assert verify_password(password="otherpassword",
                           hashed_password=hashed_password) is False
    
def test_create_access_token():
    username = "Alice"
    user_id = 1
    role = "user"
    expire_minutes = settings.access_token_expire_minutes
    expire_delta = timedelta(minutes=expire_minutes)
    
    token = create_access_token(username, user_id, role, expire_delta)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode token
    try:
        payload = jwt.decode(token=token, key=settings.secret_key, 
                            algorithms=[settings.algorithm])
    except JWTError:
        assert False, "The created token is invalid or cannot be decoded."
    
    # User info
    assert payload.get('sub') == username
    assert payload.get('id') == user_id
    assert payload.get('role') == role
    
    # Verify the expire_delta
    assert payload.get('exp') is not None
    token_exp_time = datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc)
    
    assert token_exp_time > (datetime.now(timezone.utc) + 
                             timedelta(minutes=expire_minutes - 1))
    
    assert token_exp_time < (datetime.now(timezone.utc) + 
                             timedelta(minutes=expire_minutes + 1))
    
def test_decode_access_token():
    
    # payload creation
    payload_to_encode = {
        'sub':'Alice',
        'id':1,
        'role':'user',
        'exp':datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    }
    
    # Token encoding
    test_token = jwt.encode(
        payload_to_encode, settings.secret_key, settings.algorithm
    )
    
    # decode_access_token
    decoded_token = decode_access_token(test_token)
    
    assert decoded_token['username'] == payload_to_encode['sub']
    assert decoded_token['id'] == payload_to_encode['id']
    assert decoded_token['role'] == payload_to_encode['role']
    
def test_decode_access_token_expired():
    
    # payload creation
    payload_to_encode = {
        'sub':'Alice',
        'id':1,
        'role':'user',
        'exp':datetime.now(timezone.utc) - timedelta(minutes=5)
    }
    
    expired_token = jwt.encode(
        payload_to_encode, settings.secret_key, settings.algorithm
    )
    
    # verifies that the function raises the correct exception
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(expired_token)
        
    # verifies that is credential_exception (401)
    assert exc_info.value.status_code == credential_exception.status_code
    assert exc_info.value.detail == credential_exception.detail

def test_decode_access_token_missing_value():
    
    # payload creation
    payload_to_encode = {
        'sub':'Alice',
        'id':1,
        'exp':datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    }
    
    expired_token = jwt.encode(
        payload_to_encode, settings.secret_key, settings.algorithm
    )
    
    # verifies that the function raises the correct exception
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(expired_token)
        
    # verifies that is credential_exception (401)
    assert exc_info.value.status_code == credential_exception.status_code
    assert exc_info.value.detail == credential_exception.detail
