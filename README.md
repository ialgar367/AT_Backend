# AT_Backend - Django REST API

Backend de Anitoki con Django y autenticación por sesión.

## Requisitos

- Python 3.8+

## Instalación

### 1. Crear y activar entorno virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copiar `.env.example` a `.env` y editar:

```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:

```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

### 4. Migrar base de datos

```bash
python manage.py migrate
```

### 5. (Opcional) Crear superusuario

```bash
python manage.py createsuperuser
```

## Ejecución

```bash
python manage.py runserver
```

Servidor en: **http://127.0.0.1:8000/**

## Estructura

```
AT_Backend/
├── manage.py
├── requirements.txt
├── .env.example
├── core/                      # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── context/                   # Apps del proyecto
│   ├── accounts/             # Autenticación
│   ├── manager/              # Gestión de perfiles
│   └── backoffice/           # Administración de animes
├── templates/
└── static/
```

## API Endpoints

### Autenticación
- `POST /api/auth/register/` - Registrar usuario
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/user/` - Usuario actual

### Perfiles
- `GET /api/manager/profiles/` - Listar perfiles
- `POST /api/manager/profiles/` - Crear perfil
- `GET /api/manager/profiles/<id>/` - Detalle
- `PUT /api/manager/profiles/<id>/` - Actualizar
- `DELETE /api/manager/profiles/<id>/` - Eliminar

### Animes (Admin)
- `GET /api/backoffice/animes/?page=1&page_size=20` - Listar
- `POST /api/backoffice/animes/` - Crear
- `GET /api/backoffice/animes/<id>/` - Detalle
- `PUT /api/backoffice/animes/<id>/` - Actualizar
- `DELETE /api/backoffice/animes/<id>/` - Eliminar

```bash
python manage.py migrate
```

### 5. (Opcional) Crear superusuario

```bash
python manage.py createsuperuser
```

## Ejecución

```bash
python manage.py runserver
```

Servidor en: **http://127.0.0.1:8000/**

## Tests

Ejecutar todos los tests:

```bash
python manage.py test
```

Ejecutar tests específicos:

```bash
# Solo tests de autenticación
python manage.py test context.accounts

# Con cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Estructura

```
AT_Backend/
├── manage.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── POSTGRESQL_SETUP.md
├── core/                      # Configuración principal
│   ├── settings.py           # Settings con variables de entorno
│   ├── urls.py
│   └── wsgi.py
├── context/                   # Apps del proyecto
│   ├── accounts/             # Autenticación
│   │   ├── api_views.py      # Login, registro, logout
│   │   ├── api_urls.py
│   │   └── tests.py          # Tests unitarios
│   ├── manager/              # Gestión de perfiles
│   │   ├── models.py         # Profile model
│   │   ├── api_views.py
│   │   └── urls.py
│   └── backoffice/           # Administración de animes
│       ├── models.py         # Anime, Episode models
│       ├── api_views.py      # CRUD con paginación
│       └── urls.py
├── templates/                # Templates Django
└── static/                   # Archivos estáticos

## Seguridad

- ✅ SECRET_KEY en variables de entorno
- ✅ CSRF protection habilitado
- ✅ CORS configurado
- ✅ Validaciones en modelos
- ⚠️ En producción: cambiar DEBUG=False y configurar ALLOWED_HOSTS

## API Endpoints

### Autenticación

- `POST /api/auth/register/` - Registrar usuario
- `POST /api/auth/login/` - Iniciar sesión
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/user/` - Usuario actual
- `GET /api/csrf/` - Obtener token CSRF

### Perfiles (requiere autenticación)

- `GET /api/manager/profiles/` - Listar perfiles del usuario
- `POST /api/manager/profiles/` - Crear perfil
- `GET /api/manager/profiles/<id>/` - Detalle de perfil
- `PUT /api/manager/profiles/<id>/` - Actualizar perfil
- `DELETE /api/manager/profiles/<id>/` - Eliminar perfil

### Animes (requiere admin)

- `GET /api/backoffice/animes/?page=1&page_size=20` - Listar animes (paginado)
- `POST /api/backoffice/animes/` - Crear anime
- `GET /api/backoffice/animes/<id>/` - Detalle de anime
- `PUT /api/backoffice/animes/<id>/` - Actualizar anime
- `DELETE /api/backoffice/animes/<id>/` - Eliminar anime

### Episodios

- `GET /api/backoffice/episodes/?anime_id=1&page=1` - Listar episodios (paginado)
- `POST /api/backoffice/episodes/` - Crear episodio (admin)
- `GET /api/backoffice/episodes/<id>/` - Detalle de episodio
- `PUT /api/backoffice/episodes/<id>/` - Actualizar episodio (admin)
- `DELETE /api/backoffice/episodes/<id>/` - Eliminar episodio (admin)

## Docker

Ver [DOCKER_GUIDE.md](../DOCKER_GUIDE.md) en la raíz del proyecto.

Inicio rápido:

```bash
cd ..
docker-compose up
```

## Configuración Avanzada

### PostgreSQL

Ver guía completa en [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta de Django | django-insecure-change-me |
| `DEBUG` | Modo debug | True |
| `ALLOWED_HOSTS` | Hosts permitidos | localhost,127.0.0.1 |
| `DATABASE_ENGINE` | Motor de BD | django.db.backends.sqlite3 |
| `DATABASE_NAME` | Nombre de BD | db.sqlite3 |
| `DATABASE_USER` | Usuario de BD | - |
| `DATABASE_PASSWORD` | Contraseña de BD | - |
| `DATABASE_HOST` | Host de BD | - |
| `DATABASE_PORT` | Puerto de BD | - |

## Notas de Desarrollo

- Los modelos tienen validaciones automáticas (año, rating, duración, etc.)
- La paginación está implementada en las APIs de animes y episodios
- Solo el usuario 'admin' puede gestionar animes y episodios
- Los usuarios regulares pueden gestionar sus propios perfiles
├── db.sqlite3
├── core/                    # Configuración principal
│   ├── settings.py          # Settings (CORS, CSRF, apps)
│   ├── urls.py              # URLs principales
│   └── wsgi.py
├── context/
│   └── accounts/            # App de autenticación
│       ├── api_urls.py      # Rutas API
│       ├── api_views.py     # Vistas API (JSON)
│       ├── views.py         # Vistas Django tradicionales
│       └── urls.py
├── templates/               # Templates HTML Django
└── static/                  # CSS/JS estático
```

## API Endpoints

### Salud
- `GET /api/health/` - Verificar estado de la API

### Autenticación
- `GET /api/csrf/` - Obtener cookie CSRF
- `POST /api/auth/register/` - Registrar nuevo usuario
  ```json
  {"username": "usuario", "email": "email@example.com", "password": "password123"}
  ```
- `POST /api/auth/login/` - Iniciar sesión
  ```json
  {"username": "usuario", "password": "password123"}
  ```
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/user/` - Obtener usuario actual

## Configuración CORS

El backend está configurado para aceptar requests desde:
- `http://127.0.0.1:5173`
- `http://localhost:5173`

Puedes modificar estos orígenes en `core/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5173',
    'http://localhost:5173',
]
```

## Admin Django

Accede al panel admin en: **http://127.0.0.1:8000/admin/**

## Dependencias principales

- Django 4.2+
- django-cors-headers 4.4+
