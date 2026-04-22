# 🚀 Azure Deployment Guide

## Opción 1: Azure Static Web Apps (Recomendado para SPAs)

### Requisitos
- Cuenta de Azure
- Repositorio en GitHub
- Azure CLI (opcional)

### Pasos

1. **Crear Static Web App**
   ```bash
   az staticwebapp create \
     --name soundlog-frontend \
     --resource-group my-resource-group \
     --source https://github.com/yourusername/soundlog \
     --location eastus \
     --branch main
   ```

2. **Configurar en Azure Portal**
   - Ir a Azure Portal
   - Buscar "Static Web Apps"
   - Click en "Crear"
   - Conectar tu repositorio de GitHub
   - Seleccionar rama (main/development)
   - Seleccionar framework (React)
   - Configurar rutas de build:
     - Build location: `frontend`
     - App location: `dist`
     - API location: (dejar en blanco si está en otra app)

3. **Variables de entorno**
   En Azure Portal → Configuración → Configuración de aplicación:
   ```
   VITE_API_BASE_URL=https://your-backend-api.azurewebsites.net
   ```

4. **Deploy automático**
   - Los cambios en GitHub se despliegan automáticamente
   - Verifica los logs en Azure Portal

---

## Opción 2: Azure Container Instances (con Docker)

### Requisitos
- Azure Container Registry (ACR)
- Docker Desktop
- Azure CLI

### Pasos

1. **Construir imagen Docker**
   ```bash
   docker build -t soundlog-frontend:latest .
   ```

2. **Crear Container Registry**
   ```bash
   az acr create \
     --resource-group my-resource-group \
     --name soundlogregistry \
     --sku Basic
   ```

3. **Subir imagen a ACR**
   ```bash
   az acr build \
     --registry soundlogregistry \
     --image soundlog-frontend:latest \
     .
   ```

4. **Desplegar en Container Instance**
   ```bash
   az container create \
     --resource-group my-resource-group \
     --name soundlog-frontend \
     --image soundlogregistry.azurecr.io/soundlog-frontend:latest \
     --cpu 1 \
     --memory 1 \
     --port 3000 \
     --dns-name-label soundlog-frontend \
     --registry-login-server soundlogregistry.azurecr.io \
     --registry-username <username> \
     --registry-password <password> \
     --environment-variables VITE_API_BASE_URL=https://your-api-url
   ```

---

## Opción 3: Azure App Service

### Requisitos
- App Service Plan
- Connection String del backend

### Pasos

1. **Crear App Service**
   ```bash
   az webapp create \
     --resource-group my-resource-group \
     --plan my-app-service-plan \
     --name soundlog-frontend \
     --runtime "NODE|18"
   ```

2. **Construir y desplegar**
   ```bash
   npm run build
   cd dist
   zip -r ../dist.zip .
   
   az webapp deployment source config-zip \
     --resource-group my-resource-group \
     --name soundlog-frontend \
     --src ../dist.zip
   ```

3. **Configurar App Service**
   - Ir a App Service → Configuración → Configuración de aplicación
   - Agregar variable: `VITE_API_BASE_URL=https://your-backend-api.azurewebsites.net`
   - Guardar cambios

4. **Habilitar SSL**
   - TLS/SSL settings → Certificados privados
   - Usar certificado proporcionado por Azure

---

## Opción 4: GitHub Actions (Automatizado)

### Crear workflow

1. **Crear archivo `.github/workflows/deploy.yml`**

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]
    paths: ['frontend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: npm install
      working-directory: ./frontend
    
    - name: Build
      run: npm run build
      working-directory: ./frontend
    
    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Deploy to Static Web App
      uses: azure/static-web-apps-deploy@v1
      with:
        azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
        repo_token: ${{ secrets.GITHUB_TOKEN }}
        action: 'upload'
        app_location: 'frontend/dist'
        api_location: ''
        output_location: ''
```

2. **Configurar secrets en GitHub**
   - Ir a Settings → Secrets and variables → Actions
   - Agregar: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - Agregar: `AZURE_CREDENTIALS`

---

## Configuración CORS para producción

En el backend (`backend/main.py`), actualizar CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-frontend-url.azurewebsites.net",
        "https://your-static-web-app.azurestaticapps.net",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Monitoreo y Logging

### En Azure Portal
- Application Insights → Registros
- Ver requestsy errores en tiempo real
- Configurar alertas

### Localmente
```bash
# Ver logs en vivo
az webapp log tail --resource-group my-resource-group --name soundlog-frontend

# Descargar logs
az webapp log download --resource-group my-resource-group --name soundlog-frontend
```

---

## Troubleshooting

### 404 errors en rutas de React
Asegúrate que la aplicación sirva `index.html` para todas las rutas.

En `web.config` (para App Service):
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="React Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchList">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

### CORS errors
- Verifica que el backend esté permitiendo tu dominio frontend
- Actualiza `VITE_API_BASE_URL` con la URL correcta del backend

### Problemas de autenticación
- Revisa que los tokens se estén guardando en localStorage
- Verifica que el backend retorne el token correctamente
- Limpia cookies/localStorage en el navegador

---

## Performance

Para optimizar la aplicación:

1. **Lazy loading de componentes**
   ```typescript
   const AlbumDetail = lazy(() => import('./pages/AlbumDetail'));
   ```

2. **Compresión gzip**
   - Habilitada automáticamente en Azure

3. **CDN**
   - Usar Azure CDN para servir assets estáticos

4. **Service Worker**
   - Para offline support y caching

---

## Costos estimados

- **Static Web Apps**: $0.15/GB transferencia (Free tier: 0.5GB)
- **Container Instance**: ~$10-15/mes
- **App Service**: $7-25/mes (Basic plan)
- **SQL Database**: $10-50+/mes

---

¡Lista para producción! 🚀
