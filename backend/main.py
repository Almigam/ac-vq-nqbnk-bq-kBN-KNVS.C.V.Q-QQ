"""
Soundlog API - Backend principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routes import auth

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title=os.getenv("APP_NAME", "Soundlog API"),
    description="API para reseñar álbumes y canciones",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Configurar CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    # Agregar dominio de Azure en producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)

# Rutas básicas
@app.get("/")
async def root():
    """Ruta raíz - verificar que la API está funcionando"""
    return {
        "message": "Bienvenido a Soundlog API",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check para Azure App Service"""
    return {"status": "healthy"}


# TODO: Agregar routers para:
# - /api/v1/users - Gestión de usuarios
# - /api/v1/albums - Gestión de álbumes
# - /api/v1/songs - Gestión de canciones
# - /api/v1/reviews - Reseñas


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "True") == "True"
    )
