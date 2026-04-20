"""
Configuración de la base de datos — Azure SQL Server
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings


# Crear engine para SQL Server con pyodbc
# fast_executemany=True mejora el rendimiento en inserciones masivas
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,       # verifica la conexión antes de usarla
    pool_size=5,              # conexiones simultáneas en el pool
    max_overflow=10,          # conexiones extra permitidas bajo carga
    connect_args={
        "timeout": 30         # timeout de conexión en segundos
    }
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()