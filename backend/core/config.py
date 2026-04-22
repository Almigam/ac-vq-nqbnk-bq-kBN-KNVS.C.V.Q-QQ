"""
Configuración mejorada con validaciones de seguridad
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import os
import secrets


class Settings(BaseSettings):
    """Configuración con seguridad mejorada"""

    # ─────────────────── APP ───────────────────
    app_name: str = Field(default="Soundlog API", description="Nombre de la aplicación")
    app_version: str = Field(default="1.0.0", description="Versión de la API")
    debug: bool = Field(
        default=False,
        description="Nunca True en producción"
    )

    # ─────────────────── SECURITY ───────────────────
    # CRITICAL: Cambiar en producción
    secret_key: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", None) or secrets.token_urlsafe(32),
        description="Clave secreta para JWT - DEBE cambiar en producción"
    )
    
    algorithm: str = Field(default="HS256", description="Algoritmo JWT")
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, ge=1, description="Requests por ventana")
    rate_limit_window_seconds: int = Field(default=60, ge=1, description="Ventana en segundos")
    
    # Password requirements
    min_password_length: int = Field(default=8, ge=8)
    require_uppercase: bool = Field(default=True)
    require_numbers: bool = Field(default=True)
    require_special: bool = Field(default=True)
    max_failed_login_attempts: int = Field(default=5)
    lockout_duration_minutes: int = Field(default=15)

    # ─────────────────── DATABASE ───────────────────
    database_url: str = Field(
        default="mssql+pyodbc://sa:YourPassword123!@localhost/soundlog?driver=ODBC+Driver+17+for+SQL+Server",
        description="URL de conexión a BD"
    )
    database_pool_size: int = Field(default=5, ge=1, le=20)
    database_max_overflow: int = Field(default=10, ge=0, le=50)
    database_pool_recycle: int = Field(default=3600, ge=60, description="Reciclar conexiones cada N segundos")

    # ─────────────────── CORS ───────────────────
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Orígenes permitidos separados por comas"
    )
    allow_credentials: bool = Field(default=True)
    allow_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "PATCH"])
    allow_headers: List[str] = Field(default=["*"])

    # ─────────────────── LOGGING ───────────────────
    log_level: str = Field(default="INFO", description="Nivel de logging")
    log_file: str = Field(default="logs/app.log", description="Archivo de logs")
    log_max_size_mb: int = Field(default=100, ge=1)
    log_backup_count: int = Field(default=5, ge=1)

    # ─────────────────── AZURE ───────────────────
    azure_tenant_id: str = Field(default="", description="Azure Tenant ID")
    azure_client_id: str = Field(default="", description="Azure Client ID")
    azure_client_secret: str = Field(default="", description="Azure Client Secret")
    keyvault_url: str = Field(default="", description="URL del Azure Key Vault")
    storage_account_name: str = Field(default="", description="Nombre de Storage Account")
    storage_account_key: str = Field(default="", description="Clave de Storage Account")
    
    # ─────────────────── HEADERS SEGURIDAD ───────────────────
    # HSTS, CSP, X-Frame-Options, etc.
    enable_hsts: bool = Field(default=True, description="Habilitar HSTS")
    hsts_max_age: int = Field(default=31536000, description="HSTS max-age en segundos (1 año)")
    enable_csp: bool = Field(default=True, description="Content Security Policy")

    class Config:
        env_file = ".env"
        case_sensitive = False
        # Cargar variables de ambiente incluso si no están en .env
        env_file_encoding = "utf-8"

    @validator("secret_key", pre=True, always=True)
    def validate_secret_key(cls, v):
        """Validar que secret_key sea lo suficientemente fuerte"""
        if not v or v == "change-this-in-production":
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError(
                    "SECRET_KEY debe ser una cadena fuerte y única en producción. "
                    "Genera una con: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            # En desarrollo, usar uno por defecto seguro
            return secrets.token_urlsafe(32)
        if len(v) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
        return v

    @validator("debug", pre=True)
    def validate_debug(cls, v):
        """Asegurar que debug sea False en producción"""
        if v and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("DEBUG no puede ser True en producción")
        return v

    @validator("allowed_origins", pre=True, always=True)
    def validate_origins(cls, v):
        """Validar CORS origins"""
        if isinstance(v, str):
            origins = [o.strip() for o in v.split(",")]
            # En producción, no permitir localhost
            if os.getenv("ENVIRONMENT") == "production":
                if any("localhost" in o or "127.0.0.1" in o for o in origins):
                    raise ValueError("No se pueden permitir localhost en producción")
            return ",".join(origins)
        return v

    @property
    def origins_list(self) -> List[str]:
        """Convierte string de orígenes a lista"""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def environment(self) -> str:
        """Obtener ambiente"""
        return os.getenv("ENVIRONMENT", "development")

    @property
    def is_production(self) -> bool:
        """¿Está en producción?"""
        return self.environment == "production"


# Instancia global de settings
settings = Settings()

# Validaciones en tiempo de inicialización
if settings.is_production and not settings.secret_key.startswith("$"):
    import warnings
    warnings.warn("⚠️  Asegúrate de que SECRET_KEY sea único en producción", RuntimeWarning)


settings = Settings()