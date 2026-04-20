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

    # Database — Azure SQL Server con pyodbc
    # Formato local:   mssql+pyodbc://user:pass@localhost/soundlog?driver=ODBC+Driver+17+for+SQL+Server
    # Formato Azure:   mssql+pyodbc://user:pass@server.database.windows.net/soundlog?driver=ODBC+Driver+17+for+SQL+Server
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mssql+pyodbc://sa:YourPassword123!@localhost/soundlog?driver=ODBC+Driver+17+for+SQL+Server"
    )

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-this-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS — se lee de variable de entorno en producción
    allowed_origins: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost,http://localhost:3000,http://localhost:8000"
    )

    @property
    def origins_list(self) -> List[str]:
        """Convierte la cadena de orígenes en lista"""
        return [o.strip() for o in self.allowed_origins.split(",")]

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