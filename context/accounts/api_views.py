import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PasswordResetToken


@require_GET
def health(request):
    return JsonResponse({'status': 'ok', 'message': 'Django API activa'})


def _read_json_body(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        return payload if isinstance(payload, dict) else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


@require_POST
def register_api(request):
    data = _read_json_body(request)

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not username or not email or not password:
        return JsonResponse({'detail': 'username, email y password son obligatorios.'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'detail': 'El nombre de usuario ya existe.'}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({'detail': 'El email ya está registrado.'}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    
    # Crear perfil por defecto
    from context.manager.models import Profile
    Profile.objects.create(
        user=user,
        name=username,
        avatar='/profiles/Profile1.png',
        background='',
        color='#000000'
    )
    
    # Generar tokens JWT
    refresh = RefreshToken.for_user(user)

    return JsonResponse(
        {
            'detail': 'Usuario creado correctamente.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
        status=201,
    )


@require_POST
def login_api(request):
    data = _read_json_body(request)

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    # Intentar autenticar por username
    user = authenticate(request, username=username, password=password)
    
    # Si falla y el username parece un email, buscar el username asociado
    if user is None and '@' in username:
        try:
            user_obj = User.objects.get(email=username)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    if user is None:
        return JsonResponse({'detail': 'Credenciales inválidas.'}, status=401)

    # Asegurar que el usuario tenga al menos un perfil
    from context.manager.models import Profile
    if not Profile.objects.filter(user=user).exists():
        Profile.objects.create(
            user=user,
            name=user.username,
            avatar='/profiles/Profile1.png',
            background='',
            color='#000000'
        )

    # Generar tokens JWT
    refresh = RefreshToken.for_user(user)
    
    return JsonResponse(
        {
            'detail': 'Sesión iniciada.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    )


@require_POST
def logout_api(request):
    # Con JWT, el logout se maneja en el frontend eliminando el token
    # No hay sesiones en el servidor que cerrar
    return JsonResponse({'detail': 'Sesión cerrada.'})


@require_GET
def user_api(request):
    # Con JWT, verificamos si el usuario está autenticado mediante el token
    # que se verifica automáticamente por JWTAuthentication
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False, 'user': None})

    return JsonResponse(
        {
            'isAuthenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
            },
        }
    )


@require_POST
def request_password_reset(request):
    """Solicita un reset de contraseña enviando un email al usuario"""
    data = _read_json_body(request)
    email = (data.get('email') or '').strip()

    if not email:
        return JsonResponse({'detail': 'El email es obligatorio.'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Por seguridad, no revelar si el email existe o no
        return JsonResponse({'detail': 'Te hemos enviado las instrucciones al correo. Si no lo ves, revisa tu carpeta de spam.'}, status=200)

    # Invalidar tokens anteriores no usados
    PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

    # Crear nuevo token
    reset_token = PasswordResetToken.objects.create(user=user)

    # Construir URL de reset (asumiendo que el frontend está en localhost:5174)
    frontend_url = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:5174'
    reset_url = f"{frontend_url}/reset-password?token={reset_token.token}"

    # Enviar email con diseño HTML
    html_content = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recuperación de contraseña</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1a1a2e; border-radius: 8px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background-color: #0f0f1e; padding: 30px; text-align: left;">
                                <h1 style="color: #9333ea; margin: 0; font-size: 24px; font-weight: bold;">AniToki</h1>
                            </td>
                        </tr>
                        
                        <!-- Body -->
                        <tr>
                            <td style="padding: 40px 30px; background-color: #ffffff;">
                                <h2 style="color: #333; font-size: 20px; margin: 0 0 20px 0;">Recuperación de contraseña</h2>
                                
                                <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 0 0 15px 0;">Hola,</p>
                                
                                <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 0 0 15px 0;">
                                    Hemos recibido una solicitud para restablecer la contraseña de tu cuenta de AniToki. 
                                    Si no has solicitado este cambio, por favor contacta inmediatamente con nuestro equipo de 
                                    atención al cliente en <a href="mailto:soporte@anitoki.com" style="color: #9333ea; text-decoration: none;">soporte@anitoki.com</a>
                                </p>
                                
                                <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 0 0 25px 0;">
                                    Para restablecer tu contraseña, haz clic en el siguiente botón:
                                </p>
                                
                                <table cellpadding="0" cellspacing="0" style="margin: 0 0 25px 0;">
                                    <tr>
                                        <td style="background-color: #9333ea; border-radius: 6px; padding: 14px 28px;">
                                            <a href="{reset_url}" style="color: #ffffff; text-decoration: none; font-size: 14px; font-weight: bold; display: inline-block;">Restablecer contraseña</a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #666; font-size: 12px; line-height: 1.6; margin: 0 0 10px 0;">
                                    <strong>Este enlace expirará en 24 horas.</strong>
                                </p>
                                
                                <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 0 0 10px 0;">
                                    Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos.
                                </p>
                                
                                <p style="color: #666; font-size: 14px; line-height: 1.6; margin: 0;">
                                    Saludos,<br>
                                    El equipo de AniToki
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f9f9f9; padding: 20px 30px; text-align: center; border-top: 1px solid #e0e0e0;">
                                <p style="color: #999; font-size: 11px; margin: 0 0 10px 0;">
                                    Este correo fue enviado desde una dirección que no admite respuestas. Por favor, no respondas a este mensaje.
                                </p>
                                <p style="color: #999; font-size: 11px; margin: 0;">
                                    <a href="#" style="color: #9333ea; text-decoration: none; margin: 0 10px;">Condiciones de Uso</a> &bull; 
                                    <a href="#" style="color: #9333ea; text-decoration: none; margin: 0 10px;">Política de Privacidad</a> &bull; 
                                    <a href="#" style="color: #9333ea; text-decoration: none; margin: 0 10px;">Centro de Ayuda</a>
                                </p>
                                <p style="color: #999; font-size: 11px; margin: 10px 0 0 0;">
                                    © 2026 AniToki. Todos los derechos reservados.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    '''
    
    plain_text = f'''Hola,

Hemos recibido una solicitud para restablecer la contraseña de tu cuenta de AniToki.

Para restablecer tu contraseña, haz clic en el siguiente enlace:
{reset_url}

Este enlace expirará en 24 horas.

Si no solicitaste este cambio, puedes ignorar este correo.

Saludos,
El equipo de AniToki'''

    try:
        send_mail(
            subject='Recuperación de contraseña - AniToki',
            message=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_content,
        )
    except Exception as e:
        return JsonResponse({'detail': f'Error al enviar el correo: {str(e)}'}, status=500)

    return JsonResponse({'detail': 'Te hemos enviado las instrucciones al correo. Si no lo ves, revisa tu carpeta de spam.'}, status=200)


@require_POST
def verify_reset_token(request):
    """Verifica si un token de reset es válido"""
    data = _read_json_body(request)
    token = data.get('token', '').strip()

    if not token:
        return JsonResponse({'detail': 'Token requerido.'}, status=400)

    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if reset_token.is_valid():
            return JsonResponse({
                'valid': True,
                'username': reset_token.user.username
            })
        else:
            return JsonResponse({'valid': False, 'detail': 'Token expirado o ya usado.'}, status=400)
    except PasswordResetToken.DoesNotExist:
        return JsonResponse({'valid': False, 'detail': 'Token inválido.'}, status=400)


@require_POST
def reset_password(request):
    """Resetea la contraseña usando un token válido"""
    data = _read_json_body(request)
    token = data.get('token', '').strip()
    new_password = data.get('password', '')

    if not token or not new_password:
        return JsonResponse({'detail': 'Token y contraseña son obligatorios.'}, status=400)

    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if not reset_token.is_valid():
            return JsonResponse({'detail': 'Token expirado o ya usado.'}, status=400)

        # Cambiar contraseña
        user = reset_token.user
        user.set_password(new_password)
        user.save()

        # Marcar token como usado
        reset_token.used = True
        reset_token.save()

        return JsonResponse({'detail': 'Contraseña cambiada exitosamente.'}, status=200)

    except PasswordResetToken.DoesNotExist:
        return JsonResponse({'detail': 'Token inválido.'}, status=400)
