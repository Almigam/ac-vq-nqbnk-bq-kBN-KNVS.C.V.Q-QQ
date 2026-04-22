"""
Rutas de Autenticación mejoradas con seguridad
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from core.database import get_db
from core.models import User
from core.schemas import UserCreate, UserResponse, TokenResponse
from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_user_refresh,
)
from core.security_utils import (
    password_validator,
    email_validator,
    username_validator,
    login_rate_limiter,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar nuevo usuario con validaciones de seguridad.
    
    Validaciones:
    - Email válido y único
    - Username único y válido (3-30 caracteres, solo alfanuméricos, guiones, guiones bajos)
    - Contraseña fuerte (8+ caracteres, mayúscula, número, carácter especial)
    """
    
    # Validar email
    if not email_validator.is_valid(user.email):
        logger.warning(f"Invalid email format: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Formato de email inválido"
        )
    
    email_clean = email_validator.sanitize(user.email)
    
    # Verificar email duplicado
    existing_email = db.query(User).filter(User.email == email_clean).first()
    if existing_email:
        logger.warning(f"Email already registered: {email_clean}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado"
        )
    
    # Validar username
    if not username_validator.is_valid(user.username):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username inválido. Debe tener 3-30 caracteres, solo letras, números, guiones y guiones bajos"
        )
    
    username_clean = username_validator.sanitize(user.username)
    
    # Verificar username duplicado
    existing_username = db.query(User).filter(User.username == username_clean).first()
    if existing_username:
        logger.warning(f"Username already taken: {username_clean}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario ya existe"
        )
    
    # Validar contraseña
    try:
        hashed_password = get_password_hash(user.password)
    except ValueError as e:
        logger.warning(f"Weak password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
    # Crear usuario
    new_user = User(
        email=email_clean,
        username=username_clean,
        full_name=user.full_name or "",
        hashed_password=hashed_password,
        is_active=True
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"New user registered: {username_clean}")
        return new_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar usuario"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Iniciar sesión y obtener tokens (access + refresh).
    
    Incluye:
    - Rate limiting (máximo 5 intentos fallidos por 15 minutos)
    - Validación segura de credenciales
    - Tokens JWT con expiración
    """
    
    # Rate limiting
    if login_rate_limiter.is_limited(form_data.username):
        logger.warning(f"Login rate limit exceeded for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Intenta más tarde.",
            headers={"Retry-After": "900"}  # 15 minutos en segundos
        )
    
    # Buscar usuario por email o username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    # Verificar contraseña (sempre hacer timing-safe check)
    password_correct = user is not None and verify_password(
        form_data.password,
        str(user.hashed_password)
    )
    
    if not password_correct:
        login_rate_limiter.record_attempt(form_data.username)
        logger.warning(f"Failed login attempt for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si usuario está activo
    if not user.is_active:
        logger.warning(f"Login attempt with inactive user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    
    # Crear tokens
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=7)
    )
    
    logger.info(f"Successful login for user: {user.username}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800,  # 30 minutos en segundos
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    current_user_id: int = Depends(get_current_user_refresh),
    db: Session = Depends(get_db)
):
    """
    Obtener nuevo access token usando refresh token.
    
    El refresh token tiene mayor duración y se usa
    para obtener nuevos access tokens sin re-autenticación.
    """
    
    # Verificar que el usuario existe y está activo
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no válido o inactivo"
        )
    
    # Crear nuevo access token
    new_access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )
    
    logger.debug(f"Token refreshed for user: {user.username}")
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=None,  # No refrescar el refresh token por seguridad
        token_type="bearer",
        expires_in=1800,
    )


@router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_token(current_user_id: int = Depends(get_current_user)):
    """
    Verificar que el access token es válido.
    Usado por el frontend para validar autenticación.
    """
    return {"user_id": current_user_id, "valid": True}