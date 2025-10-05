# todo_api/config.py
"""Application configuration and environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "TodoApp RESTful API"
    app_version: str = "0.1.0"
    app_description: str = "A RESTful API for managing user tasks."
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./todosapp.db"
    
    # Security - JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Security - Argon2
    argon2_time_cost: int = 2
    argon2_memory_cost: int = 65536
    argon2_parallelism: int = 4
    argon2_hash_len: int = 32
    argon2_salt_len: int = 16
    
    # CORS
    cors_origins: str = "http://localhost:8501"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='UTF-8')


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()