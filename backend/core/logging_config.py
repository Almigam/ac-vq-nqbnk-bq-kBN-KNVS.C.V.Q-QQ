"""
Logging mejorado con rotación
"""
import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging(log_file: str = "logs/app.log", level: str = "INFO", max_size_mb: int = 100, backup_count: int = 5):
    """Configurar logging con rotación de archivos"""
    
    # Crear directorio de logs si no existe
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar logger raíz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Formato detallado
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler con rotación (file)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_size_mb * 1024 * 1024,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Suprimir logs muy verbosos
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Obtener logger para un módulo"""
    return logging.getLogger(name)
