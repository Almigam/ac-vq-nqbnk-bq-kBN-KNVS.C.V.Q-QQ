# 🔐 Guía de Seguridad - Soundlog

## 📋 Índice

1. [Backend - Seguridad](#backend---seguridad)
2. [Frontend - Seguridad](#frontend---seguridad)
3. [Comunicación API](#comunicación-api)
4. [Variables de Entorno](#variables-de-entorno)
5. [Despliegue Seguro](#despliegue-seguro)
6. [Auditoría y Logging](#auditoría-y-logging)

---

## Backend - Seguridad

### 🔑 Autenticación JWT

**Mejoras implementadas:**
- ✅ Tokens access con expiración de 30 minutos
- ✅ Tokens refresh con expiración de 7 días
- ✅ Validación de tipo de token
- ✅ Timestamps de emisión (`iat` claim)
- ✅ Rate limiting en login (5 intentos/15 minutos)

**Ubicación:** `core/security.py`

```python
# Crear tokens seguros
access_token = create_access_token(
    data={"sub": str(user.id)},
    expires_delta=timedelta(minutes=30)
)
refresh_token = create_refresh_token(
    data={"sub": str(user.id)},
    expires_delta=timedelta(days=7)
)
```

### 🔐 Contraseñas

**Requisitos validados:**
- ✅ Mínimo 8 caracteres
- ✅ Al menos una mayúscula
- ✅ Al menos un número
- ✅ Al menos un carácter especial
- ✅ Hash con bcrypt (12 rondas)

**Ubicación:** `core/security_utils.py`

```python
from core.security_utils import password_validator

is_valid, error = password_validator.validate(
    password,
    min_length=8,
    require_uppercase=True,
    require_numbers=True,
    require_special=True
)
```

### 📝 Validación de Inputs

**Implementado:**
- ✅ Validación de email (RFC 5322)
- ✅ Validación de username (3-30 caracteres, alfanuméricos)
- ✅ Sanitización de texto (prevención XSS)
- ✅ Límites de longitud en payloads (10MB)
- ✅ Detección de patrones peligrosos

**Ubicación:** `core/security_utils.py`

### 🛡️ Middleware de Seguridad

**Headers de seguridad agregados:**

```
X-Frame-Options: DENY                    # Prevenir clickjacking
X-Content-Type-Options: nosniff          # Prevenir MIME sniffing
X-XSS-Protection: 1; mode=block          # Protección XSS
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
Strict-Transport-Security: max-age=31536000  # HSTS
Content-Security-Policy: default-src 'self'  # CSP
```

**Ubicación:** `core/security_middleware.py`

### 🚫 Rate Limiting

**Configurado:**
- ✅ 100 requests/minuto por defecto
- ✅ 5 intentos de login fallidos → bloqueo 15 minutos
- ✅ Límite de payload: 10MB
- ✅ Rechazo de métodos HTTP inválidos

### 📊 Auditoría y Logging

**Registra:**
- ✅ Todas las autenticaciones exitosas/fallidas
- ✅ Cambios en datos sensibles
- ✅ Errores de validación
- ✅ Intentos de acceso no autorizado
- ✅ Rotación automática de logs (100MB)

**Ubicación:** `core/logging_config.py`

---

## Frontend - Seguridad

### 🔑 Manejo de Tokens

**Mejoras implementadas:**
- ✅ Almacenamiento seguro en localStorage
- ✅ Auto-refresh de access token
- ✅ Limpieza de tokens en logout
- ✅ Interceptor para manejar expiración
- ✅ Retry automático con nuevo token

**Ubicación:** `src/api/client.ts`

```typescript
// Interceptor maneja 401 automáticamente
// Si expira el access token:
// 1. Intenta renovar con refresh token
// 2. Si falla, redirige a login
// 3. Reintenta la request original
```

### 🛡️ Validación de Formularios

**Implementado en frontend:**
- ✅ Validación en tiempo real
- ✅ Confirmación de contraseña
- ✅ Mensajes de error claros
- ✅ Deshabilitación de submit durante envío
- ✅ CSRF protection (headers)

### 🔐 Rutas Protegidas

**Componente ProtectedRoute:**

```typescript
// Solo usuarios autenticados pueden acceder
<ProtectedRoute>
  <Profile />
</ProtectedRoute>
```

**Ubicación:** `src/components/ProtectedRoute.tsx`

### 🚫 CSP Enforcement

```
- Bloquea scripts inline
- Solo scripts del mismo origen
- Previene inyección de contenido
```

---

## Comunicación API

### 🔄 Flow de Autenticación

```
┌─────────────┐
│   Login     │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│ Validar credenciales │
│ (Rate limiting)      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Crear tokens         │
│ - Access (30 min)    │
│ - Refresh (7 días)   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Guardar en frontend  │
│ (localStorage)       │
└──────────────────────┘
```

### 🔄 Refresh Token Flow

```
Access Token Expira (30 min)
         ▼
┌──────────────────┐
│ API retorna 401  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│ Frontend envía refresh   │
│ token al servidor        │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Servidor valida refresh  │
│ Retorna nuevo access     │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Reintentar request       │
│ original con nuevo token │
└──────────────────────────┘
```

### 📡 Headers Securizados

Cada request incluye:
```
Authorization: Bearer <access_token>
X-Requested-With: XMLHttpRequest
Content-Type: application/json
```

---

## Variables de Entorno

### Backend (.env)

```env
# ━━━━━━ CRÍTICO EN PRODUCCIÓN ━━━━━
ENVIRONMENT=production
SECRET_KEY=<genera_con: python -c "import secrets; print(secrets.token_urlsafe(32))">
DEBUG=False

# ━━━━━━ DATABASE ━━━━━━
DATABASE_URL=mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server

# ━━━━━━ CORS ━━━━━━
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# ━━━━━━ SEGURIDAD ━━━━━━
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_FAILED_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
MIN_PASSWORD_LENGTH=8

# ━━━━━━ AZURE ━━━━━━
AZURE_TENANT_ID=xxx
AZURE_CLIENT_ID=xxx
AZURE_CLIENT_SECRET=xxx
KEYVAULT_URL=https://xxx.vault.azure.net/

# ━━━━━━ LOGGING ━━━━━━
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Frontend (.env.local)

```env
VITE_API_BASE_URL=https://your-api-domain.com
```

---

## Despliegue Seguro

### ✅ Pre-Despliegue Checklist

**Backend:**
- [ ] `ENVIRONMENT=production`
- [ ] `SECRET_KEY` generada y única
- [ ] `DEBUG=False`
- [ ] CORS origins específicos (sin localhost)
- [ ] Database credenciales desde variables
- [ ] Logs configurados
- [ ] HTTPS habilitado
- [ ] Headers CSP/HSTS activos

**Frontend:**
- [ ] `VITE_API_BASE_URL` apunta a producción
- [ ] Sin logs sensibles en consola
- [ ] Build optimizado
- [ ] Service worker configurado

### 🔒 HTTPS Obligatorio

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert;
    ssl_certificate_key /path/to/key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Redirect HTTP to HTTPS
}

server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

### 🛡️ Firewall Rules (Azure)

```
Permitir:
- 443 (HTTPS) desde cualquier lugar
- 80 (HTTP) → redirige a 443

Bloquear:
- 8000 (Backend directo)
- 5173 (Frontend dev)
```

---

## Auditoría y Logging

### 📊 Eventos Registrados

| Evento | Nivel | Detalles |
|--------|-------|----------|
| Login exitoso | INFO | usuario, timestamp, IP |
| Login fallido | WARNING | usuario, timestamp, IP |
| Registro usuario | INFO | nuevo usuario |
| Token expirado | WARNING | usuario, timestamp |
| Rate limit excedido | WARNING | IP, endpoint |
| Cambio contraseña | INFO | usuario, timestamp |
| Acceso denegado | WARNING | usuario, recurso, razón |
| Error servidor | ERROR | tipo, stacktrace |

### 📁 Estructura de Logs

```
logs/
└── app.log          # Último log activo
    app.log.1       # Rotado (100MB)
    app.log.2
    ...
```

**Formato:**
```
2026-04-22 15:30:45 - app.auth - INFO - [auth.py:123] - Successful login for user: juan_perez
```

### 🔍 Búsqueda de Logs

```bash
# Errores en autenticación
grep "401\|Unauthorized" logs/app.log

# Intentos de login fallidos
grep "Failed login" logs/app.log

# Rate limiting
grep "rate limit" logs/app.log

# Errores del servidor
grep "ERROR" logs/app.log
```

---

## 🚨 Incidentes de Seguridad

### Si sospechas una brecha:

1. **Cambiar SECRET_KEY inmediatamente**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Invalidar todos los tokens**
   - Cambiar SECRET_KEY automáticamente invalida todos
   - Usuarios deben reloguear

3. **Revisar logs**
   ```bash
   grep "ERROR\|WARNING" logs/app.log | tail -100
   ```

4. **Reset de contraseñas**
   - Opción: forzar cambio de contraseña en próximo login

5. **Audit trail**
   - Revisar accesos sospechosos
   - Verificar cambios no autorizados

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Password Security](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [API Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_API_Security_Cheat_Sheet.html)

---

**Última actualización:** 2026-04-22
**Versión:** 1.1.0
