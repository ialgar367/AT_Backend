import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST


@require_GET
def health(request):
    return JsonResponse({'status': 'ok', 'message': 'Django API activa'})


@ensure_csrf_cookie
@require_GET
def csrf(request):
    return JsonResponse({'detail': 'CSRF cookie set'})


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
    login(request, user)

    return JsonResponse(
        {
            'detail': 'Usuario creado correctamente.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
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

    login(request, user)
    return JsonResponse(
        {
            'detail': 'Sesión iniciada.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
        }
    )


@require_POST
def logout_api(request):
    logout(request)
    return JsonResponse({'detail': 'Sesión cerrada.'})


@require_GET
def user_api(request):
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
