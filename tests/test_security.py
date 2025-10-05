from todo_api.security import hash_password, verify_password, create_access_token
from todo_api.config import settings
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

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