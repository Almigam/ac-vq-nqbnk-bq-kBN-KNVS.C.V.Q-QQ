"""
Soundlog API — Backend principal con seguridad mejorada
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
from routes import auth, users, albums, songs, reviews
from core.config import settings
from core.security_middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    AuditLoggingMiddleware,
    InputSanitizationMiddleware
)
from core.logging_config import setup_logging
import logging

# Cargar variables de ambiente
load_dotenv()

# Configurar logging
logger = setup_logging(
    log_file=settings.log_file,
    level=settings.log_level,
    max_size_mb=settings.log_max_size_mb,
    backup_count=settings.log_backup_count
)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API para reseñar álbumes y canciones",
    version=settings.app_version,
    docs_url="/api/docs" if not settings.is_production else None,  # Desactivar en producción
    openapi_url="/api/openapi.json" if not settings.is_production else None,
)

# ──────────────────── MIDDLEWARE DE SEGURIDAD ────────────────────
# Orden es importante: confiar en hosts → headers → rate limit → audit → input

# 1. Validar hosts de confianza
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.origins_list
)

# 2. CORS - permitir orígenes específicos
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
)

# 3. Headers de seguridad
app.add_middleware(SecurityHeadersMiddleware)

# 4. Rate limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.rate_limit_requests
)

# 5. Audit logging
app.add_middleware(AuditLoggingMiddleware)

# 6. Sanitización de inputs
app.add_middleware(InputSanitizationMiddleware)

# ──────────────────── ROUTERS ────────────────────
app.include_router(auth.router)       # /api/v1/auth
app.include_router(users.router)      # /api/v1/users
app.include_router(albums.router)     # /api/v1/albums
app.include_router(songs.router)      # /api/v1/songs
app.include_router(reviews.router)    # /api/v1/reviews


# ──────────────────── HEALTH CHECKS ────────────────────
@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a Soundlog API",
        "version": settings.app_version,
        "status": "online",
        "environment": settings.environment
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check para Azure App Service"""
    return {
        "status": "healthy",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness probe para Kubernetes"""
    try:
        # Verificar conexión a BD
        from core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "not_ready", "error": str(e)}, 503


# ──────────────────── ERROR HANDLERS ────────────────────
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para excepciones no manejadas"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "detail": "Error interno del servidor",
        "error_id": __import__("uuid").uuid4().hex[:8]  # Para debugging
    }, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=not settings.is_production,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )