from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, status
from todo_api.config import settings
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# =========================== Credential exception =========================== #
credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate user.",
    headers={"WWW-Authenticate": "Bearer"}
)

# ================================== Argon2 ================================== #
# Initialize the PasswordHasher using settings loaded from the application's 
# configuration
password_hasher = PasswordHasher(
    time_cost=settings.argon2_time_cost,
    memory_cost=settings.argon2_memory_cost,
    parallelism=settings.argon2_parallelism,
    hash_len=settings.argon2_hash_len,
    salt_len=settings.argon2_salt_len
)

def hash_password(password:str) -> str:
    """Hashes a plaintext password using the configured Argon2 hasher."""
    return password_hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against an Argon2 hash."""
    try:
        password_hasher.verify(hashed_password, password)
        return True
    except VerifyMismatchError:
        return False
    
# ==================================== JWT =================================== #
def create_access_token(username: str, user_id:int, role:str, expire_delta: timedelta) -> str:
    """Create a JWT access token.

    Args:
        username (str): The username of the user.
        user_id (int): The ID of the user.
        role (str): The role of the user.
        expires_delta (timedelta): The token expiration time.

    Returns:
        str: The encoded JWT token.
    """
    
    to_encode = {'sub':username, 'id':user_id, 'role':role}
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({'exp':expire})
    return jwt.encode(to_encode, settings.secret_key, settings.algorithm)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        
        if (username is None) or (user_id is None) or (role is None):
            raise credential_exception
        
        return {"username": username, "id": user_id, "role": role}
    
    except JWTError:
        raise credential_exception