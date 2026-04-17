"""
Configuración de la aplicación
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # App
    app_name: str = os.getenv("APP_NAME", "Soundlog API")
    debug: bool = os.getenv("DEBUG", "False") == "True"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/soundlog")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Azure
    azure_tenant_id: str = os.getenv("AZURE_TENANT_ID", "")
    azure_client_id: str = os.getenv("AZURE_CLIENT_ID", "")
    azure_client_secret: str = os.getenv("AZURE_CLIENT_SECRET", "")
    keyvault_url: str = os.getenv("KEYVAULT_URL", "")
    storage_account_name: str = os.getenv("STORAGE_ACCOUNT_NAME", "")
    storage_account_key: str = os.getenv("STORAGE_ACCOUNT_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
