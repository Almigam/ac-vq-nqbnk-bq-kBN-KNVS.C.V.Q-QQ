"""
Soundlog API — Backend principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routes import auth
from core.config import settings

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API para reseñar álbumes y canciones",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS dinámico — lee los orígenes de config
# En local: localhost. En Azure: URL del Blob Storage frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)

# TODO: Agregar routers para:
# - /api/v1/users   — Gestión de usuarios
# - /api/v1/albums  — Gestión de álbumes
# - /api/v1/songs   — Gestión de canciones
# - /api/v1/reviews — Reseñas


@app.get("/")
async def root():
    """Ruta raíz — verificar que la API está funcionando"""
    return {
        "message": "Bienvenido a Soundlog API",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check para Azure App Service"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )