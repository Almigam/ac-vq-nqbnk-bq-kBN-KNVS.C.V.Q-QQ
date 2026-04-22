"""
Utilitarios de seguridad y autenticación mejorados
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.config import settings
from core.security_utils import password_validator, login_rate_limiter
import logging

logger = logging.getLogger(__name__)

# Configurar hash de contraseñas con parámetros de seguridad
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Más rondas = más seguro pero más lento
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar contraseña de forma segura.
    Usa timing-safe comparison.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning(f"Error durante verificación de contraseña: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hashear contraseña.
    Validar fortaleza antes de hashear.
    """
    # Validar fortaleza
    is_valid, error_msg = password_validator.validate(
        password,
        min_length=settings.min_password_length,
        require_uppercase=settings.require_uppercase,
        require_numbers=settings.require_numbers,
        require_special=settings.require_special
    )
    
    if not is_valid:
        raise ValueError(error_msg)
    
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear JWT access token.
    El token expira automáticamente.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({
        "exp": expire,
        "type": "access",  # Identificar tipo de token
        "iat": datetime.utcnow()  # Issued at
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creando token: {str(e)}")
        raise


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear JWT refresh token.
    Válido por más tiempo, usado para obtener nuevos access tokens.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({
        "exp": expire,
        "type": "refresh",  # Identificar tipo de token
        "iat": datetime.utcnow()
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creando refresh token: {str(e)}")
        raise


def verify_token(token: str, token_type: str = "access") -> Tuple[Optional[int], Optional[str]]:
    """
    Verificar y decodificar token JWT.
    Retorna (user_id, error_message)
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Verificar tipo de token
        token_type_claim = payload.get("type")
        if token_type_claim != token_type:
            return None, "Tipo de token inválido"
        
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            return None, "Token sin información de usuario"
        
        return int(user_id), None
        
    except jwt.ExpiredSignatureError:
        return None, "Token expirado"
    except jwt.JWTError as e:
        logger.warning(f"JWT error: {str(e)}")
        return None, "Token inválido"
    except Exception as e:
        logger.error(f"Error verificando token: {str(e)}")
        return None, "Error al procesar token"


async def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    """
    Obtener ID del usuario actual desde el token JWT.
    Realiza validaciones de seguridad.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id, error = verify_token(token, token_type="access")
    if error or user_id is None:
        logger.warning(f"Unauthorized access attempt: {error}")
        raise credential_exception
    
    return user_id


async def get_current_user_refresh(token: str = Depends(oauth2_scheme)) -> int:
    """
    Obtener usuario desde refresh token.
    Usado en endpoint de refresh.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id, error = verify_token(token, token_type="refresh")
    if error or user_id is None:
        raise credential_exception
    
    return user_id