from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .models import Profile, Watchlist
from context.backoffice.models import Anime
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


@login_required
@require_http_methods(["GET", "POST"])
def watchlist(request):
    """Obtener la lista de guardados o agregar un anime"""
    # Obtener el perfil actual de la sesión
    profile_id = request.session.get('current_profile_id')
    if not profile_id:
        return JsonResponse({'error': 'No profile selected'}, status=400)
    
    try:
        profile = Profile.objects.get(pk=profile_id, user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    if request.method == "GET":
        # Obtener todos los animes en la watchlist
        watchlist_items = Watchlist.objects.filter(profile=profile).select_related('anime')
        data = [{
            'id': item.id,
            'anime': {
                'id': item.anime.id,
                'title': item.anime.title,
                'cover_image': item.anime.cover_image,
                'description': item.anime.description,
                'year': item.anime.year,
                'status': item.anime.status,
                'audio_type': item.anime.audio_type,
            },
            'added_at': item.added_at.isoformat()
        } for item in watchlist_items]
        return JsonResponse(data, safe=False)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            anime_id = data.get('anime_id')
            
            if not anime_id:
                return JsonResponse({'error': 'anime_id is required'}, status=400)
            
            anime = Anime.objects.get(pk=anime_id)
            
            # Crear o verificar si ya existe
            watchlist_item, created = Watchlist.objects.get_or_create(
                profile=profile,
                anime=anime
            )
            
            return JsonResponse({
                'success': True,
                'created': created,
                'message': 'Añadido a Mi Lista' if created else 'Ya está en Mi Lista'
            }, status=201 if created else 200)
            
        except Anime.DoesNotExist:
            return JsonResponse({'error': 'Anime not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["DELETE"])
def watchlist_remove(request, anime_id):
    """Eliminar un anime de la lista de guardados"""
    profile_id = request.session.get('current_profile_id')
    if not profile_id:
        return JsonResponse({'error': 'No profile selected'}, status=400)
    
    try:
        profile = Profile.objects.get(pk=profile_id, user=request.user)
        watchlist_item = Watchlist.objects.get(profile=profile, anime_id=anime_id)
        watchlist_item.delete()
        return JsonResponse({'success': True, 'message': 'Eliminado de Mi Lista'}, status=200)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    except Watchlist.DoesNotExist:
        return JsonResponse({'error': 'Item not in watchlist'}, status=404)
