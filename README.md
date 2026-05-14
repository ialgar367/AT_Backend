# AT_Backend - Django REST API

Backend de **AniToki**, plataforma de streaming de anime construida con Django 4.2+ y Django REST Framework 3.17+. Sistema completo con autenticación JWT, gestión de perfiles múltiples, catálogo de animes, seguimiento de progreso y recuperación de contraseña.

## Características

- ✅ **Autenticación JWT** con tokens de acceso y refresh
- ✅ **Sistema multi-perfil** (hasta 4 perfiles por usuario)
- ✅ **Gestión de animes y episodios** con panel de administración
- ✅ **Watchlist personalizada** por perfil
- ✅ **Seguimiento de progreso** de visualización
- ✅ **Streaming de video** con soporte M3U8 (HLS)
- ✅ **Recuperación de contraseña** vía email (SendGrid)
- ✅ **Paginación** en listados de animes/episodios
- ✅ **Filtros y búsqueda** de animes
- ✅ **Sistema de likes/dislikes** por episodio
- ✅ **Deployment en Render** con PostgreSQL

## Requisitos

- Python 3.11+ (recomendado 3.11.0 para producción en Render)
- PostgreSQL (producción) o SQLite (desarrollo)

## Instalación (Desarrollo Local)

### 1. Clonar el repositorio

```bash
git clone https://github.com/ialgar367/AT_Backend.git
cd AT_Backend
```

### 2. Crear y activar entorno virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar `.env.example` a `.env`:

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

Editar `.env` con tus configuraciones:

```env
# Django Core
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (desarrollo)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Email (opcional para desarrollo, requerido para password reset)
SENDGRID_API_KEY=SG.tu_api_key_aqui
DEFAULT_FROM_EMAIL=tu_email_verificado@gmail.com

# CORS (frontend)
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

> **Recuperación de contraseña**: Para que funcione el "¿Olvidaste tu contraseña?", necesitas configurar SendGrid. Ver guía completa en [SENDGRID_SETUP.md](SENDGRID_SETUP.md)

### 5. Cargar datos iniciales (opcional)

El proyecto incluye un fixture con 25 animes y 795 episodios:

```bash
python manage.py loaddata fixtures.json
```

Esto carga:
- 25 animes populares (One Piece, Demon Slayer, Attack on Titan, etc.)
- 795 episodios con URLs de video de demostración
- Videos de prueba usando streams M3U8 públicos

### 6. Migrar base de datos

```bash
python manage.py migrate
```

### 7. Crear superusuario (admin)

Opción 1: Automático (desde fixtures)
```bash
python manage.py create_superuser_auto
```
Crea: `admin` / `admin123`

Opción 2: Manual
```bash
python manage.py createsuperuser
```

## Ejecución

### Servidor de desarrollo

```bash
python manage.py runserver
```

Servidor en: **http://127.0.0.1:8000/**

### Acceder al admin de Django

- URL: http://127.0.0.1:8000/admin/
- Usuario: `admin`
- Contraseña: `admin123` (si usaste `create_superuser_auto`)

## Tecnologías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Django | 4.2+ | Framework web |
| Django REST Framework | 3.17.1 | API REST |
| djangorestframework-simplejwt | 5.5.1 | Autenticación JWT |
| PyJWT | 2.12.1 | Manejo de tokens |
| Gunicorn | 21.2.0+ | Servidor WSGI (producción) |
| WhiteNoise | 6.6.0+ | Servir archivos estáticos |
| psycopg2-binary | 2.9.9+ | Adaptador PostgreSQL |
| dj-database-url | 2.1.0+ | Configuración de BD por URL |
| python-decouple | 3.8+ | Variables de entorno |
| django-cors-headers | 4.4+ | CORS |
| sendgrid | 6.12.5+ | Envío de emails |

## Estructura del Proyecto

```
AT_Backend/
├── manage.py                   # CLI de Django
├── requirements.txt            # Dependencias Python
├── runtime.txt                 # Versión de Python para Render
├── build.sh                    # Script de build para Render
├── fixtures.json               # 25 animes + 795 episodios
├── .env.example                # Plantilla de variables de entorno
├── SENDGRID_SETUP.md          # Guía de configuración de email
│
├── core/                       # Configuración del proyecto
│   ├── settings.py            # Settings con JWT, CORS, Email
│   ├── urls.py                # URLs principales
│   ├── wsgi.py                # WSGI para Gunicorn
│   └── email_backend.py       # Backend personalizado para SendGrid
│
└── context/                    # Apps del proyecto
    │
    ├── accounts/              # Autenticación y usuarios
    │   ├── models.py         # PasswordResetToken
    │   ├── api_views.py      # Login, Register, Password Reset
    │   ├── api_urls.py       # Rutas API JWT
    │   ├── urls.py           # Rutas tradicionales Django
    │   ├── views.py          # Vistas de templates
    │   └── management/
    │       └── commands/
    │           └── create_superuser_auto.py
    │
    ├── manager/               # Gestión de perfiles
    │   ├── models.py         # Profile (avatar, name, user)
    │   ├── api_views.py      # CRUD perfiles, watchlist, progreso
    │   └── urls.py
    │
    └── backoffice/            # Catálogo de animes
        ├── models.py          # Anime, Episode, WatchProgress
        ├── api_views.py       # CRUD animes, episodios, progreso
        └── urls.py
```

## API Endpoints

### Autenticación (JWT)

#### Registro y Login

**Registro** (público - no requiere autenticación):
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "usuario",
  "email": "email@example.com",
  "password": "password123"
}

Response 201: {
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { "id": 1, "username": "usuario", "email": "..." }
}
```

**Login** (público):
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "usuario",
  "password": "password123"
}

Response 200: {
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Refresh Token**:
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response 200: {
  "access": "nuevo_access_token..."
}
```

**Usuario Actual** (requiere autenticación):
```http
GET /api/auth/user/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response 200: {
  "id": 1,
  "username": "usuario",
  "email": "email@example.com",
  "is_staff": false
}
```

#### Recuperación de Contraseña (público)

```http
POST /api/auth/password-reset/request/
Content-Type: application/json

{
  "email": "email@example.com"
}
Response 200: { "message": "Email de recuperación enviado" }
```

```http
POST /api/auth/password-reset/verify/
Content-Type: application/json

{
  "token": "abc123..."
}
Response 200: { "valid": true }
```

```http
POST /api/auth/password-reset/confirm/
Content-Type: application/json

{
  "token": "abc123...",
  "password": "nueva_password"
}
Response 200: { "message": "Contraseña actualizada" }
```

### Perfiles (requiere autenticación)

**Listar perfiles del usuario autenticado:**
```http
GET /api/manager/profiles/
Authorization: Bearer eyJ0eXAiOiJKV1Qi...

Response 200: [
  {
    "id": 1,
    "name": "Izan",
    "avatar": "profile1.png",
    "user": 1
  }
]
```

**Crear perfil:**
```http
POST /api/manager/profiles/
Authorization: Bearer eyJ0eXAiOiJKV1Qi...
Content-Type: application/json

{
  "name": "Mi Perfil",
  "avatar": "profile2.png"
}
Response 201: { "id": 2, "name": "Mi Perfil", "avatar": "profile2.png", "user": 1 }
```

**Detalle/Actualizar/Eliminar:**
```http
GET /api/manager/profiles/{id}/
PUT /api/manager/profiles/{id}/
DELETE /api/manager/profiles/{id}/
Authorization: Bearer {token}
```

### Animes

**Listar animes** (público - no requiere autenticación):
```http
GET /api/backoffice/public/animes/?page=1&page_size=20&search=one+piece

Response 200: {
  "count": 25,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": 6,
      "title": "One Piece",
      "anime_slug": "one-piece",
      "description": "...",
      "category": "Shōnen",
      "episode_count": 50,
      "status": "En emisión",
      "year": 1999,
      "studio": "Toei Animation",
      "thumbnail": "..."
    }
  ]
}
```

**CRUD Animes** (solo admin):
```http
GET /api/backoffice/animes/?page=1
POST /api/backoffice/animes/
GET /api/backoffice/animes/{id}/
PUT /api/backoffice/animes/{id}/
DELETE /api/backoffice/animes/{id}/
Authorization: Bearer {admin_token}
```

### Episodios

**Listar episodios de un anime:**
```http
GET /api/backoffice/episodes/?anime_id=6&page=1&page_size=50
Authorization: Bearer {token}

Response 200: {
  "count": 50,
  "results": [
    {
      "id": 27,
      "anime": 6,
      "episode_number": 1,
      "title": "Episodio 1",
      "description": "Romance Dawn — Se muestra la infancia...",
      "duration": 24,
      "video_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
      "thumbnail": "...",
      "created_at": "2026-04-15T15:16:56.240Z"
    }
  ]
}
```

**CRUD Episodios** (solo admin):
```http
POST /api/backoffice/episodes/
GET /api/backoffice/episodes/{id}/
PUT /api/backoffice/episodes/{id}/
DELETE /api/backoffice/episodes/{id}/
Authorization: Bearer {admin_token}
```

### Watchlist (requiere profile_id)

**Ver watchlist de un perfil:**
```http
GET /api/manager/watchlist/?profile_id=1
Authorization: Bearer {token}

Response 200: [
  {
    "id": 1,
    "profile": 1,
    "anime": {
      "id": 6,
      "title": "One Piece",
      "thumbnail": "...",
      ...
    },
    "added_at": "2026-05-13T10:30:00Z"
  }
]
```

**Agregar anime a watchlist:**
```http
POST /api/manager/watchlist/
Authorization: Bearer {token}
Content-Type: application/json

{
  "anime_id": 6,
  "profile_id": 1
}
Response 201: { "message": "Agregado a la watchlist" }
```

**Eliminar de watchlist:**
```http
DELETE /api/manager/watchlist/remove/{anime_id}/?profile_id=1
Authorization: Bearer {token}

Response 200: { "message": "Eliminado de la watchlist" }
```

### Progreso de Visualización

**Ver progreso de un anime:**
```http
GET /api/backoffice/progress/{anime_id}/?profile_id=1
Authorization: Bearer {token}

Response 200: {
  "current_episode": 5,
  "watched": false
}
```

**Actualizar progreso:**
```http
POST /api/backoffice/progress/{anime_id}/
Authorization: Bearer {token}
Content-Type: application/json

{
  "profile_id": 1,
  "current_episode": 6,
  "watched": false
}
Response 200: { "message": "Progreso actualizado" }
```

### Fuentes de Video

```http
GET /api/backoffice/consumet/sources/{anime_slug}/{episode_number}/
Authorization: Bearer {token}

Response 200: {
  "sources": [
    {
      "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
      "quality": "default",
      "isM3U8": true
    }
  ],
  "headers": {},
  "download": "",
  "source": "database"
}
```

## Seguridad

- ✅ **SECRET_KEY** en variables de entorno (nunca en código)
- ✅ **JWT** con tokens de acceso (60 min) y refresh (7 días)
- ✅ **CORS** configurado para frontend específico
- ✅ **AllowAny** solo en endpoints públicos (register, login, password-reset, public animes)
- ✅ **Autenticación por defecto** en todos los endpoints REST Framework
- ✅ **Admin-only** decoradores personalizados para operaciones sensibles
- ⚠️ **Producción**: Cambiar `DEBUG=False` y `ALLOWED_HOSTS` correctamente

## Tests

```bash
# Todos los tests
python manage.py test

# Solo accounts
python manage.py test context.accounts

# Con cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment en Render

### URLs del Proyecto

- **Backend (API)**: https://anitoki-backend.onrender.com
- **Frontend**: https://anitoki-frontend.onrender.com
- **GitHub Backend**: https://github.com/ialgar367/AT_Backend
- **GitHub Frontend**: https://github.com/ialgar367/AT_Frontend

### Configuración Automática

El proyecto está configurado para deployment automático en Render con:

**build.sh** (ejecutado en cada deploy):
```bash
#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata fixtures.json --ignorenonexistent
python manage.py create_superuser_auto
```

**runtime.txt**:
```
python-3.11.0
```

### Variables de Entorno en Render

Configurar en Dashboard → Environment:

```env
# Django Core
SECRET_KEY=generar-nueva-clave-super-segura
DEBUG=False
ALLOWED_HOSTS=anitoki-backend.onrender.com

# Database (proporcionado por Render PostgreSQL)
DATABASE_URL=postgres://user:pass@host/db

# CORS
CORS_ALLOWED_ORIGINS=https://anitoki-frontend.onrender.com

# Email (SendGrid)
SENDGRID_API_KEY=SG.tu_api_key_aqui
DEFAULT_FROM_EMAIL=tu_email_verificado@gmail.com
```

### Servicios Necesarios en Render

1. **PostgreSQL Database** (Free tier - 90 días)
2. **Web Service** para Django (Free tier - 512MB RAM)
   - Build Command: `./build.sh`
   - Start Command: `gunicorn core.wsgi:application`
   - Environment: Python 3.11.0

### Limitaciones Free Tier

- **PostgreSQL**: 90 días gratis, luego $7/mes
- **Web Service**: Sleep después de 15 minutos de inactividad
- **Builds**: Solo cuando hay cambios en GitHub

### Datos Iniciales (fixtures.json)

El archivo `fixtures.json` se carga automáticamente en cada deploy con:
- 25 animes populares
- 795 episodios
- URLs de video de demostración (M3U8)

Para actualizar datos en producción:
1. Modificar `fixtures.json` localmente
2. Commit y push a GitHub
3. Render detectará cambios y re-desplegará

### Crear Superusuario Adicional

```bash
# Desde Render Shell (requiere plan de pago)
python manage.py createsuperuser

# O automático con variables de entorno
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

## Configuración de Email (SendGrid)

Para que funcione la recuperación de contraseña:

1. Crear cuenta en [SendGrid](https://sendgrid.com/)
2. Verificar un email sender
3. Generar API Key
4. Configurar variables de entorno

Ver guía completa: [SENDGRID_SETUP.md](SENDGRID_SETUP.md)

## Arquitectura del Sistema

### Modelos de Datos

**User** (Django built-in) → **Profile** (1 a 4)
- Cada perfil tiene watchlist independiente
- Cada perfil tiene progreso de visualización independiente

**Anime** ←→ **Episode** (muchos a uno)
**Profile** ←→ **WatchProgress** ←→ **Anime**
**Profile** ←→ **Watchlist** ←→ **Anime**

### Flujo de Autenticación JWT

1. Usuario hace login → Recibe `access` y `refresh` tokens
2. Frontend guarda tokens en `localStorage`
3. Cada petición incluye header: `Authorization: Bearer {access_token}`
4. Cuando `access` expira (60 min) → Usa `refresh` para obtener nuevo `access`
5. Si `refresh` expira (7 días) → Usuario debe volver a hacer login

### Sistema Multi-Perfil

```
Usuario "juan"
  ├── Perfil "Juan" (id: 1)
  │   ├── Watchlist: [One Piece, Naruto]
  │   └── Progreso: One Piece ep 5, Naruto ep 12
  │
  ├── Perfil "María" (id: 2)
  │   ├── Watchlist: [Demon Slayer]
  │   └── Progreso: Demon Slayer ep 3
  │
  └── Perfil "Kids" (id: 3)
      ├── Watchlist: [My Hero Academia]
      └── Progreso: MHA ep 1
```

Cada endpoint de watchlist/progreso requiere `profile_id` para saber a qué perfil afecta.

## Desarrollo

### Agregar Nueva App

```bash
python manage.py startapp nueva_app
```

1. Agregar a `INSTALLED_APPS` en `settings.py`
2. Crear modelos en `models.py`
3. Crear vistas en `api_views.py`
4. Configurar URLs en `urls.py`
5. Migrar: `python manage.py makemigrations && python manage.py migrate`

### Workflow de Git

```bash
# Desarrollo local
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios ...
git add .
git commit -m "feat: descripción"
git push origin feature/nueva-funcionalidad

# Merge a main
git checkout main
git merge feature/nueva-funcionalidad
git push origin main
# Render auto-despliega al detectar push a main
```

## Licencia

Proyecto de fin de curso - AniToki 2026

## Autor

**Izan Algar** - [@ialgar367](https://github.com/ialgar367)
**Juan Gonzalez** - [@JuanGonzalez759](https://github.com/JuanGonzalez759)
