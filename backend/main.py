"""
Soundlog API — Backend principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import auth, users, albums, songs, reviews
from core.config import settings

load_dotenv()

app = FastAPI(
    title=settings.app_name,
    description="API para reseñar álbumes y canciones",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router)       # /api/v1/auth
app.include_router(users.router)      # /api/v1/users
app.include_router(albums.router)     # /api/v1/albums
app.include_router(songs.router)      # /api/v1/songs
app.include_router(reviews.router)    # /api/v1/reviews


@app.get("/")
async def root():
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