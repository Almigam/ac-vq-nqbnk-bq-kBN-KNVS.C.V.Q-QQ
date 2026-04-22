# 🎵 Soundlog Frontend - Guía de Inicio Rápido

## Requisitos previos

- Node.js 16+ instalado
- npm o yarn
- Backend de Soundlog corriendo en `http://localhost:8000`

## Instalación y ejecución

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno

Copia el archivo `.env.example` a `.env.local`:

```bash
cp .env.example .env.local
```

El archivo `.env.local` debería contener:
```
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Iniciar el servidor de desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## Pantallas principales

### 🏠 Home
- Página de bienvenida
- Información sobre Soundlog
- Links rápidos para explorar

### 🔐 Autenticación
- **Login**: Inicia sesión con tu usuario
- **Register**: Crea una nueva cuenta

### 📚 Álbumes
- Exploración de álbumes
- Vista de grid con portadas
- Detalles detallados de cada álbum
- Canciones del álbum
- Reseñas de usuarios

### 🎵 Canciones
- Listado completo de canciones
- Búsqueda por álbum
- Información de duración

### ⭐ Reseñas
- Escribe reseñas en álbumes
- Calificaciones de 1-5 estrellas
- Comentarios personalizados
- Visualiza reseñas de otros usuarios

### 👤 Perfil
- Información de tu cuenta
- Historial de tus reseñas
- Opción de cerrar sesión

## Estructura de archivos

```
frontend/
├── src/
│   ├── api/                 # Cliente HTTP y servicios API
│   │   ├── client.ts       # Configuración de axios
│   │   └── index.ts        # Endpoints y tipos
│   ├── components/          # Componentes reutilizables
│   │   ├── Navbar.tsx      # Barra de navegación
│   │   └── ProtectedRoute.tsx
│   ├── context/             # React Context
│   │   └── AuthContext.tsx
│   ├── hooks/               # Custom hooks
│   │   └── useAuth.ts
│   ├── pages/               # Páginas principales
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── AlbumsList.tsx
│   │   ├── AlbumDetail.tsx
│   │   ├── SongsList.tsx
│   │   └── Profile.tsx
│   ├── styles/              # Estilos CSS
│   ├── App.tsx             # Componente raíz
│   └── main.tsx            # Punto de entrada
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Comandos disponibles

```bash
# Desarrollo con hot reload
npm run dev

# Construir para producción
npm run build

# Previsualizar build de producción
npm run preview

# Linter
npm run lint
```

## Funcionalidades principales

### 🔑 Autenticación
- Registro con email, usuario, nombre completo y contraseña
- Login con usuario o email
- Token JWT persistente en localStorage
- Logout automático en caso de token expirado

### 🎯 API Integration
- Cliente Axios pre-configurado
- Interceptores para token JWT
- Manejo de errores centralizado
- Tipos TypeScript para todas las respuestas

### 🎨 UI/UX
- Tema oscuro moderno
- Gradientes púrpura-azul
- Animaciones suaves
- Responsive design (mobile, tablet, desktop)
- Estados de carga y error

### 🔒 Seguridad
- Rutas protegidas que requieren autenticación
- Token almacenado en localStorage
- Redirección automática a login si no autenticado

## Troubleshooting

### Error de conexión a la API
- Verifica que el backend esté corriendo en `http://localhost:8000`
- Revisa la configuración en `.env.local`
- Abre la consola del navegador para más detalles

### Problemas con autenticación
- Limpia localStorage: `localStorage.clear()` en console
- Recarga la página
- Intenta registrarte de nuevo

### Build errors
```bash
# Limpia node_modules y reinstala
rm -rf node_modules
npm install
npm run dev
```

## Próximas mejoras

- [ ] Búsqueda de álbumes y canciones
- [ ] Filtros avanzados
- [ ] Paginación mejorada
- [ ] Cargar imágenes de portadas
- [ ] Integración con Spotify/Apple Music
- [ ] Sistema de favoritos
- [ ] Recomendaciones personalizadas
- [ ] Dark/Light mode toggle

## Soporte

Para reportar bugs o sugerencias, abre un issue en el repositorio.

¡Disfruta usando Soundlog! 🎵
