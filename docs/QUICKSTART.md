# 🚀 QUICKSTART - Soundlog Setup

Guía rápida para configurar el entorno de desarrollo local.

## 📋 Requisitos Previos

### Backend
- Python 3.11 o superior
- SQL Server 2019+ (local o Azure)
- pip/virtualenv

### Frontend
- Node.js 18+
- npm o yarn

---

## ⚙️ Setup Backend

### 1. Crear Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo ejemplo
cp .env.example .env

# Editar .env con valores locales:
# - DATABASE_URL: tu conexión a SQL Server
# - SECRET_KEY: genera una clave
```

Generar SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Configurar Base de Datos

```bash
# Las migraciones se crean automáticamente con SQLAlchemy
# Asegúrate que la BD existe y el usuario tiene permisos
```

### 5. Iniciar Server

```bash
# Desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# En navegador
http://localhost:8000/docs
```

---

## ⚙️ Setup Frontend

### 1. Instalar Dependencias

```bash
cd frontend
npm install
```

### 2. Configurar Variables de Entorno

```bash
# Crear archivo local
cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Soundlog
VITE_APP_VERSION=1.0.0-dev
EOF
```

### 3. Iniciar Dev Server

```bash
npm run dev

# En navegador
http://localhost:5173
```

---

## ✅ Verificar Setup

### Backend

```bash
# Health check
curl http://localhost:8000/health

# Response esperado:
# {"status":"healthy","timestamp":"2026-04-22T..."}
```

### Frontend

```bash
# Abrir en navegador
http://localhost:5173

# Deberías ver la página de inicio
# Navegar a Login para probar
```

### Autenticación

```bash
# 1. Ir a /register
# 2. Crear usuario (ej: testuser@example.com, Contraseña123!)
# 3. Ir a /login
# 4. Ingresar credenciales
# 5. Ver tokens en localStorage (DevTools)
```

---

## 🔍 Debugging

### Backend

```bash
# Ver logs
tail -f logs/app.log

# Debug mode en config.py (solo desarrollo)
DEBUG=True
```

### Frontend

```bash
# DevTools (F12)
# Console: ver errores
# Network: ver requests/responses
# Application: ver localStorage tokens
```

---

## 🐳 Docker (Opcional)

### Build

```bash
# Backend
docker build -t soundlog-api backend/

# Frontend
docker build -t soundlog-web frontend/
```

### Run

```bash
docker-compose up -d
```

---

## 🧪 Testing

### Backend

```bash
# Instalar pytest
pip install pytest pytest-asyncio

# Crear archivo tests/test_auth.py
pytest tests/

# Con cobertura
pytest --cov=backend tests/
```

### Frontend

```bash
# Tests con Vitest
npm run test

# Coverage
npm run test:coverage
```

---

## 🔐 Seguridad - Checklist Local

- [ ] `.env` NO commiteado
- [ ] `SECRET_KEY` distinta en cada ambiente
- [ ] `DEBUG=False` en producción
- [ ] CORS origins específicos
- [ ] HTTPS en producción
- [ ] Logs monitoreados
- [ ] Backups configurados

---

## 📊 Estructura Base de Datos

### Usuario
```sql
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(30) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);
```

### Álbum
```sql
CREATE TABLE albums (
    id INT PRIMARY KEY IDENTITY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    release_year INT,
    description TEXT,
    cover_image_url VARCHAR(500),
    user_id INT FOREIGN KEY REFERENCES users(id),
    created_at DATETIME DEFAULT GETDATE()
);
```

### Canción
```sql
CREATE TABLE songs (
    id INT PRIMARY KEY IDENTITY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    album_id INT FOREIGN KEY REFERENCES albums(id),
    duration INT, -- segundos
    created_at DATETIME DEFAULT GETDATE()
);
```

### Reseña
```sql
CREATE TABLE reviews (
    id INT PRIMARY KEY IDENTITY,
    rating FLOAT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    user_id INT FOREIGN KEY REFERENCES users(id),
    album_id INT FOREIGN KEY REFERENCES albums(id),
    song_id INT FOREIGN KEY REFERENCES songs(id),
    created_at DATETIME DEFAULT GETDATE()
);
```

---

## 🆘 Troubleshooting

### Error: "No module named 'xxx'"

```bash
# Verificar venv activado
which python  # Mac/Linux
where python  # Windows

# Reinstalar requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### Error: "Connection refused" (BD)

```bash
# Verificar SQL Server está corriendo
# Verificar DATABASE_URL en .env
# Verificar credenciales
# Verificar ODBC driver instalado
```

### Error: "CORS issue"

```bash
# Verificar ALLOWED_ORIGINS en backend/.env
# Debe incluir http://localhost:5173 (desarrollo)
# Verificar VITE_API_BASE_URL en frontend/.env.local
```

### Token expirado en frontend

```bash
# Refresh automático:
# - Si falla, debería redirect a /login
# - Verificar refresh_token en localStorage
# - Intentar logout/login manual
```

---

## 📚 Documentación

- [SECURITY.md](./SECURITY.md) - Guía de seguridad
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - Estructura del proyecto
- [IMPROVEMENTS_SUMMARY.md](./IMPROVEMENTS_SUMMARY.md) - Resumen de mejoras
- [API Docs](http://localhost:8000/docs) - Swagger interactivo

---

## 🤝 Contribuir

1. Create feature branch: `git checkout -b feature/xxx`
2. Commit changes: `git commit -m "feat: descripción"`
3. Push: `git push origin feature/xxx`
4. Create PR en GitHub

### Code Style

- Backend: PEP 8 (black, flake8)
- Frontend: Prettier, ESLint

---

## 📞 Soporte

Si encuentras problemas:

1. Revisar logs: `logs/app.log`
2. Revisar console del navegador (F12)
3. Verificar variables de entorno
4. Revisar [SECURITY.md](./SECURITY.md) para flujos

---

**Última actualización:** 2026-04-22
**Versión:** 1.0.0
