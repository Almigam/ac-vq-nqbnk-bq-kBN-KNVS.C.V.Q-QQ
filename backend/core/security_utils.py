"""
Utilidades de seguridad y validación
"""
import re
from typing import List
import logging

logger = logging.getLogger(__name__)


class PasswordValidator:
    """Validar fortaleza de contraseñas"""
    
    MIN_LENGTH = 8
    
    @staticmethod
    def validate(
        password: str,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_numbers: bool = True,
        require_special: bool = True
    ) -> tuple[bool, str]:
        """
        Validar contraseña contra requisitos.
        Retorna (es_válida, mensaje_error)
        """
        if len(password) < min_length:
            return False, f"La contraseña debe tener al menos {min_length} caracteres"
        
        if require_uppercase and not re.search(r"[A-Z]", password):
            return False, "La contraseña debe contener al menos una mayúscula"
        
        if require_numbers and not re.search(r"\d", password):
            return False, "La contraseña debe contener al menos un número"
        
        if require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "La contraseña debe contener al menos un carácter especial"
        
        return True, ""


class EmailValidator:
    """Validar y sanitizar emails"""
    
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    
    @staticmethod
    def is_valid(email: str) -> bool:
        """Validar formato de email"""
        if not email or len(email) > 255:
            return False
        return bool(EmailValidator.EMAIL_REGEX.match(email))
    
    @staticmethod
    def sanitize(email: str) -> str:
        """Sanitizar email"""
        return email.strip().lower()


class UsernameValidator:
    """Validar nombres de usuario"""
    
    USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")
    RESERVED_USERNAMES = {
        "admin", "root", "system", "test", "guest", "api", "null",
        "undefined", "password", "secret", "debug", "health"
    }
    
    @staticmethod
    def is_valid(username: str) -> bool:
        """Validar nombre de usuario"""
        if not username or len(username) < 3 or len(username) > 30:
            return False
        
        if username.lower() in UsernameValidator.RESERVED_USERNAMES:
            return False
        
        return bool(UsernameValidator.USERNAME_REGEX.match(username))
    
    @staticmethod
    def sanitize(username: str) -> str:
        """Sanitizar username"""
        return username.strip()


class InputSanitizer:
    """Sanitizar inputs de usuario"""
    
    DANGEROUS_PATTERNS = [
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onload=",
        r"onclick=",
        r"<iframe",
        r"<embed",
        r"<object",
    ]
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """
        Sanitizar texto plano.
        Prevenir XSS y ataques de inyección.
        """
        if not text:
            return ""
        
        # Limitar longitud
        text = text[:max_length]
        
        # Remover caracteres de control
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")
        
        # Verificar patrones peligrosos
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Patrón peligroso detectado: {pattern}")
                raise ValueError("Contenido inválido detectado")
        
        return text.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitizar nombres de archivo"""
        # Remover rutas
        filename = filename.replace("../", "").replace("..\\", "")
        filename = filename.split("/")[-1].split("\\")[-1]
        
        # Remover caracteres especiales peligrosos
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Límite de longitud
        return filename[:255]


class RateLimitChecker:
    """Verificar rate limits"""
    
    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        self.attempts: dict = {}
    
    def is_limited(self, key: str) -> bool:
        """Verificar si está limitado"""
        from datetime import datetime, timedelta
        
        if key not in self.attempts:
            self.attempts[key] = []
        
        now = datetime.now()
        # Limpiar intentos antiguos
        self.attempts[key] = [
            attempt_time for attempt_time in self.attempts[key]
            if now - attempt_time < timedelta(minutes=self.window_minutes)
        ]
        
        return len(self.attempts[key]) >= self.max_attempts
    
    def record_attempt(self, key: str):
        """Registrar un intento"""
        from datetime import datetime
        
        if key not in self.attempts:
            self.attempts[key] = []
        
        self.attempts[key].append(datetime.now())


# Instancias globales
login_rate_limiter = RateLimitChecker(max_attempts=5, window_minutes=15)
password_validator = PasswordValidator()
email_validator = EmailValidator()
username_validator = UsernameValidator()
input_sanitizer = InputSanitizer()
