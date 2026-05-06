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
@require_http_methods(["GET"])
def watchlist_list(request):
    """
    Obtiene la lista de animes guardados del perfil actual del usuario
    """
    # Obtener el profile_id de la sesión o del query param
    profile_id = request.session.get('current_profile_id') or request.GET.get('profile_id')
    
    if not profile_id:
        return JsonResponse({'error': 'No profile selected'}, status=400)
    
    try:
        profile = Profile.objects.get(pk=profile_id, user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    # Obtener todos los animes en la watchlist
    watchlist_items = Watchlist.objects.filter(profile=profile).select_related('anime')
    
    data = [{
        'id': item.id,
        'anime': {
            'id': item.anime.id,
            'title': item.anime.title,
            'year': item.anime.year,
            'genre': item.anime.genre,
            'description': item.anime.description,
            'cover_image': item.anime.cover_image,
            'background_image': item.anime.background_image,
            'rating': float(item.anime.rating),
            'audio_type': item.anime.audio_type,
            'age_rating': item.anime.age_rating,
            'content_type': item.anime.content_type,
            'is_simulcast': item.anime.is_simulcast,
            'episode_count': item.anime.episode_count,
        },
        'added_at': item.added_at.isoformat(),
    } for item in watchlist_items]
    
    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(["POST"])
def watchlist_add(request):
    """
    Añade un anime a la watchlist del perfil
    """
    try:
        data = json.loads(request.body)
        anime_id = data.get('anime_id')
        profile_id = request.session.get('current_profile_id') or data.get('profile_id')
        
        if not profile_id:
            return JsonResponse({'error': 'No profile selected'}, status=400)
        
        if not anime_id:
            return JsonResponse({'error': 'anime_id is required'}, status=400)
        
        # Verificar que el perfil pertenece al usuario
        try:
            profile = Profile.objects.get(pk=profile_id, user=request.user)
        except Profile.DoesNotExist:
            return JsonResponse({'error': 'Profile not found'}, status=404)
        
        # Verificar que el anime existe
        try:
            anime = Anime.objects.get(pk=anime_id)
        except Anime.DoesNotExist:
            return JsonResponse({'error': 'Anime not found'}, status=404)
        
        # Crear o verificar que no existe ya
        watchlist_item, created = Watchlist.objects.get_or_create(
            profile=profile,
            anime=anime
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': 'Anime added to watchlist',
                'id': watchlist_item.id,
            }, status=201)
        else:
            return JsonResponse({
                'success': True,
                'message': 'Anime already in watchlist',
                'id': watchlist_item.id,
            }, status=200)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["DELETE"])
def watchlist_remove(request, anime_id):
    """
    Elimina un anime de la watchlist del perfil
    """
    profile_id = request.session.get('current_profile_id') or request.GET.get('profile_id')
    
    if not profile_id:
        return JsonResponse({'error': 'No profile selected'}, status=400)
    
    try:
        profile = Profile.objects.get(pk=profile_id, user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    try:
        watchlist_item = Watchlist.objects.get(profile=profile, anime_id=anime_id)
        watchlist_item.delete()
        return JsonResponse({'success': True, 'message': 'Anime removed from watchlist'}, status=200)
    except Watchlist.DoesNotExist:
        return JsonResponse({'error': 'Anime not in watchlist'}, status=404)


@login_required
@require_http_methods(["GET"])
def watchlist_check(request, anime_id):
    """
    Verifica si un anime está en la watchlist del perfil actual
    """
    profile_id = request.session.get('current_profile_id') or request.GET.get('profile_id')
    
    if not profile_id:
        return JsonResponse({'in_watchlist': False})
    
    try:
        profile = Profile.objects.get(pk=profile_id, user=request.user)
        exists = Watchlist.objects.filter(profile=profile, anime_id=anime_id).exists()
        return JsonResponse({'in_watchlist': exists})
    except Profile.DoesNotExist:
        return JsonResponse({'in_watchlist': False})
