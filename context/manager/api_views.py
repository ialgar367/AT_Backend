from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Profile, Watchlist
from context.backoffice.models import Anime
import json


@api_view(['GET', 'POST'])
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
            # Verificar límite de 4 perfiles por usuario
            profile_count = Profile.objects.filter(user=request.user).count()
            if profile_count >= 4:
                return JsonResponse({'error': 'Máximo 4 perfiles permitidos por cuenta'}, status=400)
            
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


@api_view(['GET', 'PUT', 'DELETE'])
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
        # Verificar que no sea el último perfil
        profile_count = Profile.objects.filter(user=request.user).count()
        if profile_count <= 1:
            return JsonResponse({'error': 'No puedes eliminar el último perfil'}, status=400)
        
        profile.delete()
        return JsonResponse({'success': True}, status=204)


@api_view(['GET', 'POST'])
def watchlist(request):
    """Obtener la lista de guardados o agregar un anime"""
    # Obtener el perfil actual desde query params (GET) o body (POST)
    if request.method == "GET":
        profile_id = request.GET.get('profile_id')
    else:
        try:
            data = json.loads(request.body)
            profile_id = data.get('profile_id')
        except:
            profile_id = None
    
    if not profile_id:
        return JsonResponse({'error': 'profile_id is required'}, status=400)
    
    try:
        profile = Profile.objects.get(pk=profile_id, user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    if request.method == "GET":
        try:
            # Obtener todos los animes en la watchlist
            watchlist_items = Watchlist.objects.filter(profile=profile).select_related('anime')
            data = []
            
            for item in watchlist_items:
                try:
                    anime_data = {
                        'id': item.id,
                        'anime': {
                            'id': item.anime.id,
                            'title': item.anime.title,
                            'cover_image': item.anime.cover_image,
                            'description': item.anime.description or '',
                            'year': item.anime.year,
                            'audio_type': getattr(item.anime, 'audio_type', 'SUB'),
                            'content_type': getattr(item.anime, 'content_type', 'SERIE'),
                        },
                        'added_at': item.added_at.isoformat()
                    }
                    data.append(anime_data)
                except Exception as item_error:
                    print(f"Error processing watchlist item {item.id}: {str(item_error)}")
                    continue
            
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"Error loading watchlist: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': 'Error loading watchlist', 'detail': str(e)}, status=500)
    
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


@api_view(['POST'])
def select_profile(request):
    """Seleccionar un perfil y guardarlo en la sesión"""
    try:
        data = json.loads(request.body)
        profile_id = data.get('profile_id')
        
        if not profile_id:
            return JsonResponse({'error': 'profile_id is required'}, status=400)
        
        # Verificar que el perfil pertenece al usuario
        profile = Profile.objects.get(pk=profile_id, user=request.user)
        
        # Guardar en la sesión
        request.session['current_profile_id'] = profile_id
        
        return JsonResponse({
            'success': True,
            'profile': {
                'id': profile.id,
                'name': profile.name,
                'avatar': profile.avatar,
                'background': profile.background,
                'color': profile.color,
            }
        })
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_view(['DELETE'])
def watchlist_remove(request, anime_id):
    """Eliminar un anime de la lista de guardados"""
    profile_id = request.GET.get('profile_id')
    if not profile_id:
        return JsonResponse({'error': 'profile_id is required'}, status=400)
    
    try:
        profile = Profile.objects.get(pk=profile_id, user=request.user)
        watchlist_item = Watchlist.objects.get(profile=profile, anime_id=anime_id)
        watchlist_item.delete()
        return JsonResponse({'success': True, 'message': 'Eliminado de Mi Lista'}, status=200)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    except Watchlist.DoesNotExist:
        return JsonResponse({'error': 'Item not in watchlist'}, status=404)
