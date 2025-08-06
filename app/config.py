from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/pokemon_rater.db"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Admin credentials
    admin_username: str = "admin"
    admin_password: str = "admin123"  # Change this in production
    
    # PokeAPI
    pokeapi_base_url: str = "https://pokeapi.co/api/v2"
    
    class Config:
        env_file = ".env"


settings = Settings()