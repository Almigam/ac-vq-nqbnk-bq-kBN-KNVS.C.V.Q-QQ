# 🔄 FLUJOS DE SEGURIDAD - Soundlog

## 1. Flujo de Registro

```
┌─────────────────────────────────────────────────────────────────┐
│ REGISTRO DE USUARIO                                             │
└─────────────────────────────────────────────────────────────────┘

Frontend (Register.tsx)
    │
    ├─ Validar localmente:
    │  └─ Email format OK? Username OK? Password strong?
    │
    ├─ POST /api/v1/auth/register
    │   {
    │     "email": "usuario@example.com",
    │     "username": "usuario",
    │     "password": "SecurePass123!",
    │     "full_name": "Juan Pérez"
    │   }
    ▼
Backend (routes/auth.py - register())
    │
    ├─ ✅ Validar email:
    │   └─ Formato RFC 5322
    │   └─ No existe en BD
    │
    ├─ ✅ Validar username:
    │   └─ 3-30 caracteres
    │   └─ Alfanuméricos + guión/underscore
    │   └─ No es palabra reservada
    │   └─ No existe en BD
    │
    ├─ ✅ Validar password:
    │   ├─ 8+ caracteres
    │   ├─ 1+ mayúscula
    │   ├─ 1+ número
    │   └─ 1+ carácter especial
    │
    ├─ 🔐 Hash contraseña:
    │   └─ bcrypt + 12 rondas
    │
    ├─ 💾 Crear usuario en BD
    │   └─ INSERT INTO users...
    │
    ├─ 📝 Log evento:
    │   └─ "New user registered: usuario@example.com"
    │
    └─ Retorno 201 Created
        {
          "id": 1,
          "email": "usuario@example.com",
          "username": "usuario",
          "created_at": "2026-04-22T10:30:00Z"
        }
    ▼
Frontend
    │
    └─ Redirigir a /login
```

---

## 2. Flujo de Login

```
┌─────────────────────────────────────────────────────────────────┐
│ AUTENTICACIÓN - LOGIN                                           │
└─────────────────────────────────────────────────────────────────┘

Frontend (Login.tsx)
    │
    ├─ POST /api/v1/auth/login
    │   {
    │     "email_or_username": "usuario@example.com",
    │     "password": "SecurePass123!"
    │   }
    ▼
Backend (routes/auth.py - login())
    │
    ├─ 🚫 Rate Limiting:
    │   ├─ ¿5+ intentos fallidos en 15 min?
    │   ├─ SÍ → Retorno 429 Too Many Requests
    │   └─ NO → Continuar
    │
    ├─ 🔍 Buscar usuario:
    │   ├─ Búsqueda case-insensitive por email O username
    │   ├─ Usuario no existe?
    │   │   └─ Retorno 401 Unauthorized
    │   └─ Usuario existe:
    │       ├─ ¿is_active == True?
    │       ├─ NO → Retorno 401
    │       └─ SÍ → Continuar
    │
    ├─ 🔑 Verificar contraseña:
    │   ├─ Comparación timing-safe con bcrypt
    │   ├─ Incorrecta?
    │   │   └─ Log evento + Retorno 401
    │   └─ Correcta:
    │       └─ Continuar
    │
    ├─ 🎟️ Crear tokens JWT:
    │   ├─ ACCESS TOKEN (30 minutos):
    │   │   {
    │   │     "sub": "1",
    │   │     "type": "access",
    │   │     "iat": 1713780600,
    │   │     "exp": 1713782400
    │   │   }
    │   │
    │   └─ REFRESH TOKEN (7 días):
    │       {
    │         "sub": "1",
    │         "type": "refresh",
    │         "iat": 1713780600,
    │         "exp": 1714385400
    │       }
    │
    ├─ 📝 Log evento:
    │   └─ "Successful login for user: usuario (IP: 192.168.1.1)"
    │
    └─ Retorno 200 OK
        {
          "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
          "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
          "token_type": "bearer",
          "expires_in": 1800
        }
    ▼
Frontend (AuthContext)
    │
    ├─ localStorage.setItem('access_token', token)
    ├─ localStorage.setItem('refresh_token', token)
    ├─ localStorage.setItem('user', userData)
    ├─ setUser(userData)
    │
    └─ Redirigir a /albums
```

---

## 3. Flujo de Request Autenticado

```
┌─────────────────────────────────────────────────────────────────┐
│ REQUEST AUTENTICADO - GET /albums                               │
└─────────────────────────────────────────────────────────────────┘

Frontend (AlbumsList.tsx)
    │
    ├─ GET /api/v1/albums
    ├─ Interceptor agrega header:
    │   Authorization: Bearer <access_token>
    │
    ├─ Límite de payload: 10MB ✅
    ├─ Timeout: 30 segundos ✅
    │
    └─ Enviar request
    ▼
Backend (main.py - Middleware Stack)
    │
    ├─ 1️⃣ TrustedHostMiddleware:
    │   └─ Validar Host header
    │
    ├─ 2️⃣ CORSMiddleware:
    │   └─ Verificar Origin en ALLOWED_ORIGINS
    │
    ├─ 3️⃣ SecurityHeadersMiddleware:
    │   └─ Agregar headers de seguridad
    │
    ├─ 4️⃣ RateLimitMiddleware:
    │   └─ ¿>100 req/min desde esta IP?
    │   ├─ SÍ → 429 Too Many Requests
    │   └─ NO → Continuar
    │
    ├─ 5️⃣ AuditLoggingMiddleware:
    │   └─ Registrar request (IP, path, método)
    │
    ├─ 6️⃣ InputSanitizationMiddleware:
    │   └─ Validar payload < 10MB
    │
    └─ → Route Handler (GET /albums)
    ▼
Backend (routes/albums.py)
    │
    ├─ 🔐 Dependency: get_current_user
    │   ├─ Extraer token del header Authorization
    │   ├─ Validar JWT:
    │   │   ├─ Firma válida?
    │   │   ├─ Expirado?
    │   │   ├─ type == "access"?
    │   │   └─ NO a cualquiera → 401 Unauthorized
    │   │
    │   ├─ Buscar usuario en BD
    │   ├─ Usuario existe?
    │   ├─ Usuario activo?
    │   └─ Retornar objeto User
    │
    ├─ ✅ Usuario autenticado validado
    │
    ├─ 💾 Query a BD:
    │   └─ SELECT * FROM albums WHERE user_id = current_user.id
    │
    ├─ 📝 Log evento:
    │   └─ "User (id=1) fetched albums"
    │
    └─ Retorno 200 OK
        {
          "data": [
            {
              "id": 1,
              "title": "Abbey Road",
              "artist": "The Beatles",
              ...
            }
          ]
        }
    ▼
Frontend (Interceptor)
    │
    ├─ Recibir respuesta
    ├─ ¿Status 401?
    │   └─ Intenta refresh (ver flujo 4)
    │
    └─ Renderizar datos
```

---

## 4. Flujo de Refresh Token

```
┌─────────────────────────────────────────────────────────────────┐
│ REFRESH TOKEN - Cuando access expira                            │
└─────────────────────────────────────────────────────────────────┘

Frontend (GET /albums con access token expirado)
    │
    ├─ Backend retorna: 401 Unauthorized
    ▼
Axios Interceptor (client.ts)
    │
    ├─ Detectar error 401
    ├─ ¿Ya intentamos refresh?
    │   └─ SÍ → Redirect a /login
    │   └─ NO → Continuar
    │
    ├─ ¿refresh_token existe?
    │   ├─ NO → Limpiar tokens, redirect a /login
    │   └─ SÍ → Continuar
    │
    ├─ POST /api/v1/auth/refresh
    │   {
    │     Headers: Authorization: Bearer <refresh_token>
    │   }
    ▼
Backend (routes/auth.py - refresh())
    │
    ├─ 🔐 Dependency: get_current_user_refresh
    │   ├─ Extraer refresh_token
    │   ├─ Validar JWT:
    │   │   ├─ Firma válida?
    │   │   ├─ Expirado?
    │   │   ├─ type == "refresh"? ⚠️ IMPORTANTE
    │   │   └─ NO → 401 Unauthorized
    │   │
    │   ├─ Buscar usuario
    │   └─ Usuario activo?
    │
    ├─ 🎟️ Crear NUEVO access_token:
    │   {
    │     "sub": "1",
    │     "type": "access",
    │     "iat": 1713781500,
    │     "exp": 1713783300
    │   }
    │
    ├─ ⚠️ NO renovar refresh_token (seguridad)
    │
    ├─ 📝 Log evento:
    │   └─ "Token refresh for user: usuario"
    │
    └─ Retorno 200 OK
        {
          "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
          "token_type": "bearer",
          "expires_in": 1800
        }
    ▼
Frontend (Axios)
    │
    ├─ localStorage.setItem('access_token', new_token)
    ├─ Actualizar header de la request original
    ├─ Reintentar GET /albums CON NUEVO TOKEN
    │
    └─ Recibir respuesta exitosa (200)
        └─ Renderizar datos
```

---

## 5. Flujo de Logout

```
┌─────────────────────────────────────────────────────────────────┐
│ LOGOUT                                                          │
└─────────────────────────────────────────────────────────────────┘

Frontend (Profile.tsx - Click Logout Button)
    │
    ├─ Llamar AuthContext.logout()
    ▼
AuthContext
    │
    ├─ localStorage.removeItem('access_token')
    ├─ localStorage.removeItem('refresh_token')
    ├─ localStorage.removeItem('user')
    ├─ setUser(null)
    │
    └─ Redirect a /login
        └─ ✅ Usuario completamente desconectado
```

---

## 6. Validaciones en Contraseñas

```
┌─────────────────────────────────────────────────────────────────┐
│ VALIDACIÓN DE CONTRASEÑA                                        │
└─────────────────────────────────────────────────────────────────┘

Input: "MyPassword123!"

├─ ✅ Longitud >= 8 caracteres
│   └─ "MyPassword123!" tiene 14 caracteres
│
├─ ✅ Contiene mayúscula (A-Z)
│   └─ Tiene: M, P
│
├─ ✅ Contiene minúscula (a-z)
│   └─ Tiene: yassword
│
├─ ✅ Contiene número (0-9)
│   └─ Tiene: 123
│
├─ ✅ Contiene especial (!@#$%^&*)
│   └─ Tiene: !
│
└─ ✅ CONTRASEÑA VÁLIDA
    └─ Proceder a bcrypt hash

Input: "weak"

├─ ❌ Longitud < 8 caracteres
│   └─ "weak" tiene 4 caracteres
│
└─ ❌ CONTRASEÑA RECHAZADA
    └─ Mostrar error: "Password must be at least 8 characters..."
```

---

## 7. Rate Limiting - Login Fallido

```
┌─────────────────────────────────────────────────────────────────┐
│ RATE LIMITING - 5 intentos fallidos → Bloqueo 15 min           │
└─────────────────────────────────────────────────────────────────┘

Usuario: usuario@example.com
IP: 192.168.1.100

Intento 1: POST /login ❌ Contraseña incorrecta
    └─ Log: Failed login attempt 1/5

Intento 2: POST /login ❌ Contraseña incorrecta
    └─ Log: Failed login attempt 2/5

Intento 3: POST /login ❌ Contraseña incorrecta
    └─ Log: Failed login attempt 3/5

Intento 4: POST /login ❌ Contraseña incorrecta
    └─ Log: Failed login attempt 4/5

Intento 5: POST /login ❌ Contraseña incorrecta
    └─ Log: Failed login attempt 5/5
    └─ 🔒 CUENTA BLOQUEADA POR 15 MINUTOS

Intento 6 (1 minuto después): POST /login
    └─ Retorno: 429 Too Many Requests
    └─ Mensaje: "Account locked. Try again in 14 minutes"

⏳ Esperar 15 minutos...

Intento 7 (15 min después): POST /login ✅
    └─ Intento fallido anterior limpió
    └─ Contador reinicia a 1/5
```

---

## 8. Validación de Email

```
┌─────────────────────────────────────────────────────────────────┐
│ VALIDACIÓN Y SANITIZACIÓN DE EMAIL                              │
└─────────────────────────────────────────────────────────────────┘

Input: "  USUARIO@EXAMPLE.COM  "

├─ Trim (remover espacios)
│   └─ "USUARIO@EXAMPLE.COM"
│
├─ Lowercase (convertir a minúscula)
│   └─ "usuario@example.com"
│
├─ Validar formato RFC 5322
│   └─ Contiene @? Dominio válido?
│   └─ ✅ VÁLIDO
│
├─ Verificar no exista en BD
│   └─ SELECT * FROM users WHERE email = 'usuario@example.com'
│   └─ ❌ YA EXISTE
│
└─ Retorno: 400 Bad Request
    {
      "detail": "Email already registered"
    }

Input: "usuario@example.com"

├─ Trim, Lowercase, Validar formato
│   └─ ✅ VÁLIDO y NUEVO
│
└─ Proceder a crear usuario
```

---

## 9. Sanitización XSS

```
┌─────────────────────────────────────────────────────────────────┐
│ PREVENCIÓN DE XSS EN DESCRIPCIONES                              │
└─────────────────────────────────────────────────────────────────┘

Input (JSON): 
{
  "description": "<script>alert('xss')</script> Great album"
}

Backend InputSanitizer:

├─ Detectar patrón peligroso: <script>
│   └─ ❌ BLOQUEADO
│
├─ Detectar patrón: javascript:
│   └─ ❌ BLOQUEADO
│
├─ Detectar patrón: onerror=
│   └─ ❌ BLOQUEADO
│
└─ Retorno: 400 Bad Request
    {
      "detail": "Input contains potentially malicious content"
    }

Input (JSON):
{
  "description": "Great album with beautiful artwork"
}

├─ Sin patrones peligrosos
├─ Longitud <= 1000 caracteres
├─ Remover caracteres de control
│   └─ ✅ VÁLIDO
│
└─ Guardar en BD
```

---

## 10. Headers de Seguridad

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADERS DE SEGURIDAD AGREGADOS A TODAS LAS RESPUESTAS           │
└─────────────────────────────────────────────────────────────────┘

Response Headers:

X-Frame-Options: DENY
  └─ Prevenir clickjacking
  └─ No permitir iframe desde otros sitios

X-Content-Type-Options: nosniff
  └─ Prevenir MIME type sniffing
  └─ El navegador respeta el Content-Type

X-XSS-Protection: 1; mode=block
  └─ Protección XSS del navegador
  └─ Bloquear si detecta XSS

Content-Security-Policy: default-src 'self'
  └─ Solo scripts del mismo origen
  └─ Bloquear inyección de contenido

Strict-Transport-Security: max-age=31536000
  └─ HSTS: Forzar HTTPS por 1 año
  └─ Navegador siempre usa HTTPS

Referrer-Policy: strict-origin-when-cross-origin
  └─ Control de información referrer
  └─ Privacidad del usuario

Permissions-Policy: geolocation=(), microphone=(), camera=()
  └─ Desabilitar APIs peligrosas
```

---

**Diagrama completo de seguridad - Soundlog 2026**
