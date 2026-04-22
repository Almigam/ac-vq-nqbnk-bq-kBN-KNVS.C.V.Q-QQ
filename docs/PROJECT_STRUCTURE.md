# 📁 Estructura del Proyecto Soundlog - Mejorada

## 🎯 Organización General

```
Soundlog/
├── backend/                 # API FastAPI
├── frontend/               # React/TypeScript
├── infraestructure/        # Terraform para Azure
├── docs/                   # Documentación
├── SECURITY.md             # Guía de seguridad
├── README.md               # Documentación general
└── .gitignore
```

---

## 📦 Backend Structure

```
backend/
├── main.py                 # Aplicación principal con middleware
├── requirements.txt        # Dependencias Python
├── .env.example           # Ejemplo variables de entorno
│
├── core/
│   ├── __init__.py
│   ├── config.py          # ✨ Config mejorada con validaciones
│   ├── database.py        # Conexión a BD
│   ├── models.py          # Modelos SQLAlchemy
│   ├── schemas.py         # ✨ Esquemas Pydantic mejorados
│   ├── security.py        # ✨ Funciones JWT mejoradas
│   ├── security_utils.py  # ✨ Validadores y sanitizadores
│   ├── security_middleware.py  # ✨ Middleware de seguridad
│   └── logging_config.py  # ✨ Configuración de logs
│
├── routes/
│   ├── __init__.py
│   ├── auth.py            # ✨ Autenticación mejorada
│   ├── users.py           # Usuarios
│   ├── albums.py          # Álbumes
│   ├── songs.py           # Canciones
│   └── reviews.py         # Reseñas
│
└── logs/                   # Archivos de log (rotados)
    └── app.log
```

### Cambios Principales en Backend

**✨ = Mejorado/Nuevo**

1. **config.py** - Validaciones de seguridad
   - Validar SECRET_KEY
   - No permitir debug en producción
   - Validar CORS origins
   - Configuración flexible con Pydantic

2. **security.py** - Autenticación robusta
   - Tokens access + refresh
   - Validación de tipo de token
   - Timestamps en tokens
   - Mejor manejo de errores

3. **security_utils.py** - Nuevo
   - `PasswordValidator` - validar fortaleza
   - `EmailValidator` - validar emails
   - `UsernameValidator` - validar usernames
   - `InputSanitizer` - prevenir XSS
   - `RateLimitChecker` - implementación simple

4. **security_middleware.py** - Nuevo
   - Headers de seguridad (CSP, HSTS, etc)
   - Rate limiting
   - Audit logging
   - Sanitización de inputs

5. **logging_config.py** - Nuevo
   - Logging rotado
   - Configuración centralizada
   - Niveles de log

6. **schemas.py** - Validaciones mejoradas
   - Validators para emails/passwords/usernames
   - Límites de longitud
   - Sanitización de datos
   - TokenResponse schema

7. **auth.py** - Rutas mejoradas
   - Rate limiting
   - Validaciones en cada paso
   - Refresh token endpoint
   - Verify token endpoint
   - Mejor logging

8. **main.py** - Middleware y manejo
   - Middleware de seguridad aplicado
   - Exception handlers
   - Health checks mejorados
   - Logging configurado

---

## 💻 Frontend Structure

```
frontend/
├── src/
│   ├── App.tsx            # Router principal
│   ├── main.tsx           # Punto de entrada
│   │
│   ├── api/
│   │   ├── client.ts      # ✨ Cliente Axios mejorado
│   │   └── index.ts       # Servicios API
│   │
│   ├── components/
│   │   ├── Navbar.tsx     # Navegación
│   │   └── ProtectedRoute.tsx  # Rutas protegidas
│   │
│   ├── context/
│   │   └── AuthContext.tsx  # ✨ Context mejorado
│   │
│   ├── hooks/
│   │   └── useAuth.ts     # Hook de autenticación
│   │
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── AlbumsList.tsx
│   │   ├── AlbumDetail.tsx
│   │   ├── SongsList.tsx
│   │   └── Profile.tsx
│   │
│   └── styles/
│       ├── global.css
│       ├── Navbar.css
│       ├── Auth.css
│       ├── Home.css
│       ├── Albums.css
│       ├── AlbumDetail.css
│       ├── Songs.css
│       └── Profile.css
│
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .env.local              # ✨ Nuevo
├── .gitignore
└── README.md
```

### Cambios Principales en Frontend

**✨ = Mejorado/Nuevo**

1. **client.ts** - Cliente HTTP seguro
   - Timeout configurado (30s)
   - Límite de payload (10MB)
   - Interceptor de refresh token
   - Manejo de rate limiting
   - Headers de seguridad

2. **AuthContext.tsx** - Context mejorado
   - Estado de carga
   - Auto-refresh de token
   - Verificación de autenticación al iniciar
   - Método refresh separado
   - Validación de token al cargar app

3. **.env.local** - Nuevo
   - Configuración por ambiente
   - No commitear tokens/secrets

---

## 🔐 Seguridad por Capa

### Layer 1: Network
```
┌─────────────────────────────────┐
│ HTTPS/TLS 1.2+                 │
│ - Encriptación en transito     │
│ - Certificado válido           │
└─────────────────────────────────┘
```

### Layer 2: API Gateway
```
┌─────────────────────────────────┐
│ Rate Limiting                   │
│ - 100 req/min por defecto      │
│ - 5 login intentos/15 min      │
│ CORS                            │
│ - Solo orígenes permitidos     │
└─────────────────────────────────┘
```

### Layer 3: Autenticación
```
┌─────────────────────────────────┐
│ JWT + Refresh Token             │
│ - Access: 30 minutos            │
│ - Refresh: 7 días               │
│ - Tipo de token validado        │
└─────────────────────────────────┘
```

### Layer 4: Validación
```
┌─────────────────────────────────┐
│ Input Validation                │
│ - Email, Username, Password     │
│ - Límites de longitud          │
│ - Caracteres permitidos         │
│ Sanitización                    │
│ - Prevención XSS               │
│ - Detección de patrones        │
└─────────────────────────────────┘
```

### Layer 5: Autorización
```
┌─────────────────────────────────┐
│ Rutas Protegidas                │
│ - Requieren autenticación       │
│ - Validación de usuario         │
└─────────────────────────────────┘
```

### Layer 6: Data
```
┌─────────────────────────────────┐
│ Contraseñas                     │
│ - Hash con bcrypt (12 rondas)   │
│ - Mínimo 8 caracteres          │
│ - Complejidad requerida         │
└─────────────────────────────────┘
```

---

## 📊 Flujos de Datos

### Registro de Usuario

```
Frontend           Backend              Database
   │                  │                    │
   │─ POST /register──>│                    │
   │                  │─ Validar email    │
   │                  │─ Validar username │
   │                  │─ Validar password │
   │                  │─ Hash password    │
   │                  │─ Crear usuario───>│
   │                  │<───────────────────│
   │<─ 201 Created────│                    │
   │                  │                    │
```

### Login

```
Frontend           Backend              Database
   │                  │                    │
   │─ POST /login────>│                    │
   │                  │─ Rate limit check │
   │                  │─ Buscar usuario──>│
   │                  │<───────────────────│
   │                  │─ Validar pwd      │
   │                  │─ Crear access JWT │
   │                  │─ Crear refresh JWT│
   │<─ 200 + Tokens───│                    │
   │                  │                    │
```

### Request Autenticado

```
Frontend           Backend              Database
   │                  │                    │
   │─ GET /albums    │
   │  (+ access JWT) ─>│                    │
   │                  │─ Verificar token  │
   │                  │─ Extraer user_id  │
   │                  │─ Autorizar        │
   │                  │─ Ejecutar query──>│
   │                  │<───────────────────│
   │<─ 200 + Data─────│                    │
   │                  │                    │
```

---

## 🚀 Requisitos por Ambiente

### Desarrollo
- Python 3.11+
- Node.js 18+
- SQL Server local o Azure
- .env con valores test

### Producción
- HTTPS obligatorio
- SECRET_KEY única
- DEBUG = False
- CORS restrictivo
- Logs rotados
- Azure Key Vault
- Monitoring activo

---

## 📦 Dependencias Clave

### Backend
```
fastapi==0.104.1          # Framework web
sqlalchemy==2.0.23        # ORM
python-jose==3.3.0        # JWT
passlib==1.7.4           # Password hashing
pydantic==2.5.0          # Validación
uvicorn==0.24.0          # ASGI server
```

### Frontend
```
react==18.2.0            # UI Framework
react-router-dom==6.16.0 # Routing
axios==1.6.0            # HTTP Client
typescript==5.2.2       # Type safety
vite==4.5.0             # Build tool
```

---

## 🔄 CI/CD Recommendations

```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Backend Security
        run: |
          pip install -r backend/requirements.txt
          # Ejecutar tests de seguridad
      - name: Frontend Security
        run: |
          cd frontend
          npm install
          npm run lint
```

---

**Creado:** 2026-04-22
**Versión:** 2.0.0 (Mejorada)
