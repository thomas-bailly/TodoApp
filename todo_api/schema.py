from pydantic import BaseModel, Field, EmailStr


class CreateUserRequest(BaseModel):
    """Schema for user registration request.
    
    Validates user input when creating a new account. Optional fields 
    (first_name, last_name, phone_number) can be omitted.
    
    Attributes:
        username: Unique username (3-50 characters)
        email: Valid email address (5-100 characters)
        password: Plain text password (6-100 characters), will be hashed
        first_name: Optional first name (1-50 characters)
        last_name: Optional last name (1-50 characters)
        phone_number: Optional phone number (10-15 characters)
        role: User role, typically 'user' or 'admin' (3-20 characters)
    """   
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(min_length=5, max_length=100)
    password: str = Field(min_length=6, max_length=100)
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    phone_number: str | None = Field(default=None, min_length=10, max_length=15)
    role : str = Field(min_length=3, max_length=20)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "Alice",
                "email": "Alice@email.com",
                "password": "strongpassword",
                "role": "user"
            }
        }
    }
    
class UpdateUserRequest(BaseModel):
    """Schema for updating user data. All fields are optional and nullable.
    
    Attributes:
        username: New unique username (optional).
        email: New valid email address (optional).
        first_name: New optional first name.
        last_name: New optional last name.
        phone_number: New optional phone number.
    """
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, min_length=5, max_length=100)
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    phone_number: str | None = Field(default=None, min_length=10, max_length=15)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "new.email@mail.com",
                "first_name": "New Name"
            }
        }
    }

class UpdatePasswordRequest(BaseModel):
    """Schema for updating a user's password.
    
    Attributes:
        old_password: The user's current password, required for verification.
        new_password: The new password to be set.
    """
    old_password: str = Field(min_length=6, max_length=100)
    new_password: str = Field(min_length=6, max_length=100)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "old_password": "strongpassword",
                "new_password": "newstrongpassword"
            }
        }
    }

class UserOutput(BaseModel):
    """Schema for user data returned to the client (excluding sensitive info).
    
    Attributes:
        id: The unique identifier of the user.
        username: Unique username.
        email: Valid email address.
        first_name: Optional first name.
        last_name: Optional last name.
        phone_number: Optional phone number.
        role: User role.
        
    Note: 'hashed_password' and other internal fields are excluded.
    """
    id: int
    username: str
    email: EmailStr
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    role : str
    
    # Configure Pydantic to map ORM attributes to fields
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "Alice",
                "email": "Alice@email.com",
                "role": "user"
            }
        }
    }
    
class Message(BaseModel):
    """Schema representing a simple response message.

    Attributes:
        message (str): The content of the response message, typically used for 
        success, error or info.
    """
    message: str
    
class TokenOutput(BaseModel):
    """Schema for JWT authentification token response.
    
    Attributes:
        access_token (str): The JWT access token string.
        token_type (str): The type of the token, typically "bearer".
    """
    access_token: str
    token_type: str