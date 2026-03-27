from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .models import Profile
import json


@login_required
@require_http_methods(["GET", "POST"])
def profile_list(request):
    if request.method == "GET":
        profiles = Profile.objects.filter(user=request.user)
        data = [{
            'id': profile.id,
            'name': profile.name,
            'avatar': profile.avatar,
            'background': profile.background,
            'color': profile.color,
        } for profile in profiles]
        return JsonResponse(data, safe=False)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            profile = Profile.objects.create(
                user=request.user,
                name=data.get('name'),
                avatar=data.get('avatar', '/profiles/Profile1.png'),
                background=data.get('background', ''),
                color=data.get('color', '#000000'),
            )
            return JsonResponse({
                'id': profile.id,
                'name': profile.name,
                'avatar': profile.avatar,
                'background': profile.background,
                'color': profile.color,
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET", "PUT", "DELETE"])
def profile_detail(request, pk):
    try:
        profile = Profile.objects.get(pk=pk, user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    if request.method == "GET":
        return JsonResponse({
            'id': profile.id,
            'name': profile.name,
            'avatar': profile.avatar,
            'background': profile.background,
            'color': profile.color,
        })
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            profile.name = data.get('name', profile.name)
            profile.avatar = data.get('avatar', profile.avatar)
            profile.background = data.get('background', profile.background)
            profile.color = '#000000'  # Mantener siempre el borde negro
            profile.save()
            return JsonResponse({
                'id': profile.id,
                'name': profile.name,
                'avatar': profile.avatar,
                'background': profile.background,
                'color': profile.color,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        profile.delete()
        return JsonResponse({'success': True}, status=204)
