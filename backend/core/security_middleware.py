"""
Middleware de seguridad
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict
import logging
import json

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Agregar headers de seguridad a todas las respuestas"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevenir clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevenir MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Habilitar XSS protection en navegadores
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (Feature Policy)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (HTTPS Strict Transport Security)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # CSP (Content Security Policy)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting simple por IP"""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = datetime.now()
        
        # Inicializar si no existe
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Limpiar requests antiguos (>1 minuto)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Verificar límite
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Demasiadas solicitudes. Intenta más tarde."}
            )
        
        # Registrar request
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.requests[client_ip])
        )
        
        return response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Registrar todas las acciones importantes para auditoría"""

    async def dispatch(self, request: Request, call_next):
        # Información de la request
        client_ip = request.client.host
        method = request.method
        path = request.url.path
        
        # Log antes
        logger.info(
            f"[REQUEST] {method} {path} from {client_ip}",
            extra={
                "client_ip": client_ip,
                "method": method,
                "path": path,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        response = await call_next(request)
        
        # Log después con status
        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            f"[RESPONSE] {method} {path} - Status: {response.status_code}",
            extra={
                "client_ip": client_ip,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Validar y sanitizar inputs"""

    async def dispatch(self, request: Request, call_next):
        # Rechazar requests con payloads muy grandes
        if request.headers.get("content-length"):
            try:
                content_length = int(request.headers["content-length"])
                # Límite: 10MB
                if content_length > 10 * 1024 * 1024:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"detail": "Payload demasiado grande"}
                    )
            except ValueError:
                pass
        
        # Rechazar métodos no permitidos para ciertos endpoints
        if request.method not in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]:
            return JSONResponse(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                content={"detail": "Método no permitido"}
            )
        
        response = await call_next(request)
        return response
