# Configuración de SendGrid para Recuperación de Contraseña

La funcionalidad de recuperación de contraseña de AniToki utiliza **SendGrid** para enviar correos electrónicos. Esta guía te ayudará a configurar SendGrid tanto en desarrollo local como en producción (Render).

## 📋 Tabla de Contenidos

- [¿Por qué SendGrid?](#por-qué-sendgrid)
- [Crear cuenta en SendGrid](#crear-cuenta-en-sendgrid)
- [Obtener API Key](#obtener-api-key)
- [Configurar localmente](#configurar-localmente)
- [Configurar en Render](#configurar-en-render)
- [Verificar correo remitente](#verificar-correo-remitente)
- [Solución de problemas](#solución-de-problemas)

---

## ¿Por qué SendGrid?

SendGrid es un servicio de envío de correos transaccionales que ofrece:
- ✅ **100 correos gratis al día** (suficiente para proyectos de curso)
- ✅ Configuración simple con API Key
- ✅ No requiere servidor SMTP
- ✅ Alta tasa de entrega (evita spam)

---

## Crear cuenta en SendGrid

1. Ve a [SendGrid](https://sendgrid.com/) y haz clic en **"Start for Free"**
2. Completa el formulario de registro:
   - Nombre
   - Email (usa tu correo de estudiante si tienes)
   - Contraseña
3. **Verifica tu email** haciendo clic en el enlace que te envían
4. Completa el onboarding (puedes saltar las preguntas opcionales)

---

## Obtener API Key

### Paso 1: Crear API Key

1. En el dashboard de SendGrid, ve a **Settings → API Keys**
2. Haz clic en **"Create API Key"**
3. Dale un nombre descriptivo: `AniToki Password Reset`
4. Selecciona **"Full Access"** (o al menos permisos de envío de correo)
5. Haz clic en **"Create & View"**

### Paso 2: Guardar API Key

⚠️ **IMPORTANTE**: Copia la API Key inmediatamente y guárdala en un lugar seguro. **No podrás verla de nuevo**.

Ejemplo de API Key:
```
SG.aBcDeFgHiJkLmNoPqRsTuVwXyZ.1234567890aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
```

---

## Configurar localmente

### Opción 1: Archivo `.env` (Recomendado)

1. Abre tu archivo `.env` en la raíz del backend:

```bash
# AT_Backend/.env
SENDGRID_API_KEY=SG.tu_api_key_aqui
DEFAULT_FROM_EMAIL=noreply@anitoki.com
```

2. Reemplaza `SG.tu_api_key_aqui` con tu API Key real

### Opción 2: Variables de entorno del sistema

**Windows (PowerShell):**
```powershell
$env:SENDGRID_API_KEY="SG.tu_api_key_aqui"
$env:DEFAULT_FROM_EMAIL="noreply@anitoki.com"
```

**Linux/macOS:**
```bash
export SENDGRID_API_KEY="SG.tu_api_key_aqui"
export DEFAULT_FROM_EMAIL="noreply@anitoki.com"
```

---

## Configurar en Render

### Paso 1: Ir a Environment

1. Abre tu servicio backend en Render: `https://dashboard.render.com/`
2. Selecciona tu servicio `anitoki-backend`
3. Ve a la pestaña **"Environment"**

### Paso 2: Agregar variables

Haz clic en **"Add Environment Variable"** y agrega:

| Key | Value |
|-----|-------|
| `SENDGRID_API_KEY` | `SG.tu_api_key_real_aqui` |
| `DEFAULT_FROM_EMAIL` | `noreply@anitoki.com` |

### Paso 3: Guardar y redeploy

1. Haz clic en **"Save Changes"**
2. Render hará un redeploy automático
3. Espera 2-3 minutos a que termine

---

## Verificar correo remitente

SendGrid requiere que **verifiques el dominio o email remitente** para enviar correos.

### Opción 1: Single Sender Verification (Más fácil)

1. En SendGrid, ve a **Settings → Sender Authentication**
2. Haz clic en **"Verify a Single Sender"**
3. Completa el formulario:
   - **From Name**: AniToki
   - **From Email**: Tu correo personal verificado (ej: `tu_email@gmail.com`)
   - **Reply To**: El mismo correo
   - **Company**: AniToki (opcional)
   - **Address**: Dirección ficticia
4. Haz clic en **"Create"**
5. **Verifica tu correo** haciendo clic en el enlace que te envían

### Opción 2: Domain Authentication (Avanzado)

Solo si tienes un dominio propio. Para proyectos de curso, usa **Single Sender Verification**.

### Actualizar DEFAULT_FROM_EMAIL

Después de verificar, actualiza la variable con tu correo verificado:

**Localmente (.env):**
```bash
DEFAULT_FROM_EMAIL=tu_email_verificado@gmail.com
```

**En Render:**
- Ve a Environment
- Edita `DEFAULT_FROM_EMAIL`
- Cambia a tu email verificado
- Save Changes

---

## Solución de problemas

### Error 401: Unauthorized

**Causa**: API Key incorrecta o no configurada

**Solución**:
1. Verifica que `SENDGRID_API_KEY` esté en `.env` (local) o Environment (Render)
2. Asegúrate de haber copiado la API Key completa (incluyendo el prefijo `SG.`)
3. Crea una nueva API Key si es necesario

### Error 403: Forbidden

**Causa**: Email remitente no verificado

**Solución**:
1. Ve a SendGrid → Settings → Sender Authentication
2. Verifica que tu correo esté en la lista de "Verified Senders"
3. Si no está, haz Single Sender Verification
4. Actualiza `DEFAULT_FROM_EMAIL` con el correo verificado

### No recibo el correo

**Posibles causas**:

1. **Revisa spam/correo no deseado**: SendGrid a veces cae en spam la primera vez
2. **Email incorrecto**: Verifica que el email del usuario sea correcto
3. **Límite de envíos**: Cuenta gratuita tiene límite de 100 correos/día
4. **Logs de SendGrid**: Ve a SendGrid → Activity para ver si se envió

### Error al enviar correo localmente

**Causa**: Variables de entorno no cargadas

**Solución**:
```bash
# Reinicia el servidor Django
python manage.py runserver
```

---

## Prueba rápida

### Desde la interfaz web

1. Ve a tu aplicación: `http://localhost:5173` (local) o `https://anitoki-frontend.onrender.com` (producción)
2. Haz clic en **"¿Has olvidado tu contraseña?"**
3. Introduce un email de prueba (debe ser un usuario existente)
4. Haz clic en **"Enviar instrucciones"**
5. Revisa tu bandeja de entrada (y spam)

### Desde la terminal (Django shell)

```python
python manage.py shell

# Importar Django mail
from django.core.mail import send_mail
from django.conf import settings

# Enviar correo de prueba
send_mail(
    subject='Prueba AniToki',
    message='Este es un correo de prueba.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['tu_email@gmail.com'],
    fail_silently=False,
)
```

Si ves **"1"** en la consola, el correo se envió correctamente. Si hay un error, revisa la configuración.

---

## Plan gratuito de SendGrid

| Característica | Límite |
|----------------|--------|
| Correos por día | 100 |
| Correos por mes | ~3,000 |
| Validez | Permanente |
| Precio | $0 |

**Perfecto para proyectos de curso** 🎓

---

## Alternativas (si no quieres usar SendGrid)

### 1. Email de consola (solo desarrollo)

En `settings.py`, cambia:

```python
# Reemplazar
EMAIL_BACKEND = 'core.email_backend.SendGridBackend'

# Por
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Los correos se mostrarán en la consola en lugar de enviarse.

### 2. Gmail SMTP (no recomendado)

Requiere configurar "App Passwords" en Gmail y es más complejo. SendGrid es más simple.

---

## Resumen rápido

```bash
# 1. Crear cuenta en SendGrid (gratis)
https://sendgrid.com/

# 2. Crear API Key
Settings → API Keys → Create API Key

# 3. Verificar email remitente
Settings → Sender Authentication → Verify a Single Sender

# 4. Configurar localmente
# .env
SENDGRID_API_KEY=SG.tu_api_key
DEFAULT_FROM_EMAIL=tu_email_verificado@gmail.com

# 5. Configurar en Render
Dashboard → anitoki-backend → Environment → Add Environment Variable

# 6. ¡Listo! 🎉
```

---

## Soporte

Si tienes problemas:
1. Revisa los logs de Render: `View Logs` en tu servicio
2. Revisa SendGrid Activity: SendGrid → Email Activity
3. Verifica que las variables de entorno estén configuradas correctamente

---

**¿Listo para enviar correos?** 📧 Sigue esta guía paso a paso y tendrás la recuperación de contraseña funcionando en minutos.
