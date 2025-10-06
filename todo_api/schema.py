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