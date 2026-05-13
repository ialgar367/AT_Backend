from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.core.paginator import Paginator, EmptyPage
from .models import Anime, Episode, WatchProgress
import json
import requests
from django.core.cache import cache
from functools import wraps


def admin_only(view_func):
    """Decorador para permitir solo al usuario 'admin'"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if request.user.username != 'admin':
            return JsonResponse({'error': 'Access denied. Admin only.'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_anime_dislikes(request, pk):
    if request.method == "GET":
        # Obtener parámetros de paginación
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # Validar page_size
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20
        
        animes = Anime.objects.all()
        paginator = Paginator(animes, page_size)
        
        try:
            page_obj = paginator.get_page(page)
        except EmptyPage:
            page_obj = paginator.get_page(1)
        
        data = [{
            'id': anime.id,
            'title': anime.title,
            'year': anime.year,
            'genre': anime.genre,
            'description': anime.description,
            'cover_image': anime.cover_image,
            'background_image': anime.background_image,
            'rating': float(anime.rating),
            'audio_type': anime.audio_type,
            'age_rating': anime.age_rating,
            'is_simulcast': anime.is_simulcast,
            'episode_count': anime.episode_count,
            'anime_slug': anime.anime_slug,
            'created_at': anime.created_at.isoformat(),
            'likes': anime.likes,
            'dislikes': anime.dislikes,
        } for anime in page_obj]
        
        return JsonResponse({
            'results': data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }, safe=False)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            anime = Anime.objects.create(
                title=data.get('title'),
                year=data.get('year'),
                genre=data.get('genre'),
                description=data.get('description'),
                cover_image=data.get('cover_image', ''),
                background_image=data.get('background_image', ''),
                rating=data.get('rating', 0.0),
                audio_type=data.get('audio_type', 'SUB'),
                age_rating=data.get('age_rating', 'TV-14'),
                is_simulcast=data.get('is_simulcast', False),
                episode_count=data.get('episode_count', 0),
                created_by=request.user,
            )
            return JsonResponse({
                'id': anime.id,
                'title': anime.title,
                'year': anime.year,
                'genre': anime.genre,
                'description': anime.description,
                'cover_image': anime.cover_image,
                'background_image': anime.background_image,
                'rating': float(anime.rating),
                'audio_type': anime.audio_type,
                'age_rating': anime.age_rating,
                'is_simulcast': anime.is_simulcast,
                'episode_count': anime.episode_count,
                'anime_slug': anime.anime_slug,
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@admin_only
@api_view(['GET', 'PUT', 'DELETE'])
def anime_detail(request, pk):
    try:
        anime = Anime.objects.get(pk=pk)
    except Anime.DoesNotExist:
        return JsonResponse({'error': 'Anime not found'}, status=404)
    
    if request.method == "GET":
        return JsonResponse({
            'id': anime.id,
            'title': anime.title,
            'year': anime.year,
            'genre': anime.genre,
            'description': anime.description,
            'cover_image': anime.cover_image,
            'background_image': anime.background_image,
            'rating': float(anime.rating),
            'audio_type': anime.audio_type,
            'age_rating': anime.age_rating,
            'is_simulcast': anime.is_simulcast,
            'episode_count': anime.episode_count,
            'anime_slug': anime.anime_slug,
            'likes': anime.likes,
            'dislikes': anime.dislikes,
        })
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            anime.title = data.get('title', anime.title)
            anime.year = data.get('year', anime.year)
            anime.genre = data.get('genre', anime.genre)
            anime.description = data.get('description', anime.description)
            anime.cover_image = data.get('cover_image', anime.cover_image)
            anime.background_image = data.get('background_image', anime.background_image)
            anime.rating = data.get('rating', anime.rating)
            anime.audio_type = data.get('audio_type', anime.audio_type)
            anime.age_rating = data.get('age_rating', anime.age_rating)
            anime.is_simulcast = data.get('is_simulcast', anime.is_simulcast)
            anime.episode_count = data.get('episode_count', anime.episode_count)
            anime.save()
            return JsonResponse({
                'id': anime.id,
                'title': anime.title,
                'year': anime.year,
                'genre': anime.genre,
                'description': anime.description,
                'cover_image': anime.cover_image,
                'background_image': anime.background_image,
                'rating': float(anime.rating),
                'audio_type': anime.audio_type,
                'age_rating': anime.age_rating,
                'is_simulcast': anime.is_simulcast,
                'episode_count': anime.episode_count,
                'anime_slug': anime.anime_slug,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        anime.delete()
        return JsonResponse({'success': True}, status=204)


@api_view(['GET', 'POST'])
def episode_list(request):
    if request.method == "GET":
        # Obtener parámetros de paginación y filtros
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        anime_id = request.GET.get('anime_id')
        
        # Validar page_size
        if page_size > 200:
            page_size = 200
        if page_size < 1:
            page_size = 50
        
        if anime_id:
            episodes = Episode.objects.filter(anime_id=anime_id)
        else:
            episodes = Episode.objects.all()
        
        paginator = Paginator(episodes, page_size)
        
        try:
            page_obj = paginator.get_page(page)
        except EmptyPage:
            page_obj = paginator.get_page(1)
        
        data = [{
            'id': episode.id,
            'anime_id': episode.anime.id,
            'episode_number': episode.episode_number,
            'title': episode.title,
            'description': episode.description,
            'duration': episode.duration,
            'video_url': episode.video_url,
            'thumbnail': episode.thumbnail,
        } for episode in page_obj]
        
        return JsonResponse({
            'results': data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
    
    elif request.method == "POST":
        if request.user.username != 'admin':
            return JsonResponse({'error': 'Permission denied. Admin only.'}, status=403)
        
        try:
            data = json.loads(request.body)
            episode = Episode.objects.create(
                anime_id=data.get('anime_id'),
                episode_number=data.get('episode_number'),
                title=data.get('title'),
                description=data.get('description', ''),
                duration=data.get('duration'),
                video_url=data.get('video_url', ''),
                thumbnail=data.get('thumbnail', ''),
            )
            return JsonResponse({
                'id': episode.id,
                'anime_id': episode.anime.id,
                'episode_number': episode.episode_number,
                'title': episode.title,
                'description': episode.description,
                'duration': episode.duration,
                'video_url': episode.video_url,
                'thumbnail': episode.thumbnail,
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def episode_detail(request, pk):
    try:
        episode = Episode.objects.get(pk=pk)
    except Episode.DoesNotExist:
        return JsonResponse({'error': 'Episode not found'}, status=404)
    
    if request.method == "GET":
        return JsonResponse({
            'id': episode.id,
            'anime_id': episode.anime.id,
            'episode_number': episode.episode_number,
            'title': episode.title,
            'description': episode.description,
            'duration': episode.duration,
            'video_url': episode.video_url,
            'thumbnail': episode.thumbnail,
        })
    
    elif request.method == "PUT":
        if request.user.username != 'admin':
            return JsonResponse({'error': 'Permission denied. Admin only.'}, status=403)
        
        try:
            data = json.loads(request.body)
            episode.episode_number = data.get('episode_number', episode.episode_number)
            episode.title = data.get('title', episode.title)
            episode.description = data.get('description', episode.description)
            episode.duration = data.get('duration', episode.duration)
            episode.video_url = data.get('video_url', episode.video_url)
            episode.thumbnail = data.get('thumbnail', episode.thumbnail)
            episode.save()
            return JsonResponse({
                'id': episode.id,
                'anime_id': episode.anime.id,
                'episode_number': episode.episode_number,
                'title': episode.title,
                'description': episode.description,
                'duration': episode.duration,
                'video_url': episode.video_url,
                'thumbnail': episode.thumbnail,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        if request.user.username != 'admin':
            return JsonResponse({'error': 'Permission denied. Admin only.'}, status=403)
        
        episode.delete()
        return JsonResponse({'success': True}, status=204)


# ========== ENDPOINTS PÚBLICOS PARA USUARIOS ==========

@api_view(['GET'])
@permission_classes([AllowAny])
def public_anime_detail(request, pk):
    """Endpoint público para que todos los usuarios vean detalles de un anime"""
    try:
        anime = Anime.objects.get(pk=pk)
    except Anime.DoesNotExist:
        return JsonResponse({'error': 'Anime not found'}, status=404)
    
    return JsonResponse({
        'id': anime.id,
        'title': anime.title,
        'year': anime.year,
        'genre': anime.genre,
        'description': anime.description,
        'cover_image': anime.cover_image,
        'background_image': anime.background_image,
        'rating': float(anime.rating),
        'audio_type': anime.audio_type,
        'age_rating': anime.age_rating,
        'is_simulcast': anime.is_simulcast,
        'episode_count': anime.episode_count,
        'anime_slug': anime.anime_slug,
        'likes': anime.likes,
        'dislikes': anime.dislikes,
    })

# Endpoint para actualizar likes
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_anime_likes(request, pk):
    """Actualizar el número de likes de un anime"""
    try:
        anime = Anime.objects.get(pk=pk)
    except Anime.DoesNotExist:
        return JsonResponse({'error': 'Anime not found'}, status=404)
    try:
        data = json.loads(request.body)
        likes = int(data.get('likes', anime.likes))
        if likes < 0:
            return JsonResponse({'error': 'Likes cannot be negative'}, status=400)
        anime.likes = likes
        anime.save()
        return JsonResponse({'id': anime.id, 'likes': anime.likes})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ========== JIKAN API INTEGRATION ==========

JIKAN_BASE_URL = "https://api.jikan.moe/v4"

@admin_only
@api_view(['GET'])
def jikan_search(request):
    """Buscar animes en Jikan API (MyAnimeList)"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)
    
    # Cache key basada en la búsqueda (sanitizar para evitar caracteres especiales)
    cache_key = f'jikan_search_{query.replace(" ", "_")}'
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return JsonResponse(cached_result)
    
    try:
        # Llamar a Jikan API
        response = requests.get(
            f"{JIKAN_BASE_URL}/anime",
            params={'q': query, 'limit': 10},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Transformar datos de Jikan a nuestro formato
            results = []
            for anime in data.get('data', []):
                # Extraer géneros
                genres = ', '.join([g['name'] for g in anime.get('genres', [])[:3]])
                
                # Obtener año
                year = anime.get('year') or (
                    anime.get('aired', {}).get('prop', {}).get('from', {}).get('year')
                )
                
                # Manejar score que puede ser None
                score = anime.get('score')
                rating = round(score, 1) if score is not None else 0.0
                
                results.append({
                    'mal_id': anime.get('mal_id'),
                    'title': anime.get('title'),
                    'title_english': anime.get('title_english'),
                    'year': year,
                    'genre': genres or 'Sin género',
                    'description': anime.get('synopsis', ''),
                    'cover_image': anime.get('images', {}).get('jpg', {}).get('large_image_url', ''),
                    'background_image': anime.get('images', {}).get('jpg', {}).get('large_image_url', ''),
                    'rating': rating,
                    'episodes': anime.get('episodes'),
                    'status': anime.get('status'),
                })
            
            result = {'results': results}
            
            # Cachear por 1 hora
            cache.set(cache_key, result, 3600)
            
            return JsonResponse(result)
        
        elif response.status_code == 429:
            return JsonResponse({
                'error': 'Jikan API rate limit exceeded. Please try again in a few seconds.',
                'message': 'La API de MyAnimeList está limitando las solicitudes. Intenta de nuevo en unos segundos.'
            }, status=429)
        
        else:
            return JsonResponse({
                'error': f'Jikan API error: {response.status_code}',
                'message': f'Error al conectar con MyAnimeList API (código {response.status_code})'
            }, status=response.status_code)
    
    except requests.exceptions.Timeout:
        return JsonResponse({
            'error': 'Jikan API timeout',
            'message': 'La API de MyAnimeList no respondió a tiempo. Por favor, intenta de nuevo.'
        }, status=504)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'error': f'Connection error: {str(e)}',
            'message': 'Error de conexión con MyAnimeList API. Verifica tu conexión a internet.'
        }, status=503)
    except Exception as e:
        return JsonResponse({
            'error': f'Unexpected error: {str(e)}',
            'message': 'Error inesperado al procesar la búsqueda.'
        }, status=500)


@admin_only
@api_view(['GET'])
def jikan_anime_detail(request, mal_id):
    """Obtener detalles completos de un anime desde Jikan API"""
    cache_key = f'jikan_anime_{mal_id}'
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return JsonResponse(cached_result)
    
    try:
        response = requests.get(
            f"{JIKAN_BASE_URL}/anime/{mal_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            anime = response.json().get('data', {})
            
            # Extraer géneros
            genres = ', '.join([g['name'] for g in anime.get('genres', [])])
            
            # Obtener año
            year = anime.get('year') or (
                anime.get('aired', {}).get('prop', {}).get('from', {}).get('year')
            )
            
            # Manejar score que puede ser None
            score = anime.get('score')
            rating = round(score, 1) if score is not None else 0.0
            
            result = {
                'mal_id': anime.get('mal_id'),
                'title': anime.get('title'),
                'title_english': anime.get('title_english'),
                'year': year,
                'genre': genres or 'Sin género',
                'description': anime.get('synopsis', ''),
                'cover_image': anime.get('images', {}).get('jpg', {}).get('large_image_url', ''),
                'background_image': anime.get('images', {}).get('jpg', {}).get('large_image_url', ''),
                'rating': rating,
                'episodes': anime.get('episodes'),
                'status': anime.get('status'),
                'duration': anime.get('duration'),
                'studios': ', '.join([s['name'] for s in anime.get('studios', [])]),
            }
            
            # Cachear por 24 horas
            cache.set(cache_key, result, 86400)
            
            return JsonResponse(result)
        
        elif response.status_code == 429:
            return JsonResponse({
                'error': 'Jikan API rate limit exceeded. Please try again later.'
            }, status=429)
        
        else:
            return JsonResponse({
                'error': f'Jikan API error: {response.status_code}'
            }, status=response.status_code)
    
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Jikan API timeout'}, status=504)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Connection error: {str(e)}'}, status=503)

# Vista pública para que todos los usuarios puedan ver los animes
@api_view(['GET'])
@permission_classes([AllowAny])
def public_anime_list(request):
    """Endpoint público para listar y buscar animes disponibles"""
    # Obtener parámetros de paginación y búsqueda
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    search_query = request.GET.get('search', '').strip()
    
    # Validar page_size
    if page_size > 100:
        page_size = 100
    if page_size < 1:
        page_size = 20
    
    # Obtener todos los animes
    animes = Anime.objects.all()
    
    # Filtrar por búsqueda si se proporciona
    if search_query:
        from django.db.models import Q
        animes = animes.filter(
            Q(title__icontains=search_query) |
            Q(genre__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        # Ordenar por rating cuando hay búsqueda
        animes = animes.order_by('-rating', '-created_at')
    else:
        # Orden por defecto
        animes = animes.order_by('-created_at')
    
    paginator = Paginator(animes, page_size)
    
    try:
        page_obj = paginator.get_page(page)
    except EmptyPage:
        page_obj = paginator.get_page(1)
    
    data = [{
        'id': anime.id,
        'title': anime.title,
        'year': anime.year,
        'genre': anime.genre,
        'description': anime.description,
        'cover_image': anime.cover_image,
        'background_image': anime.background_image,
        'rating': float(anime.rating),
        'anime_slug': anime.anime_slug,
        'audio_type': anime.audio_type,
        'age_rating': anime.age_rating,
        'is_simulcast': anime.is_simulcast,
        'episode_count': anime.episode_count,
    } for anime in page_obj]

    return JsonResponse({
        'results': data,
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }, safe=False)


# ===== VIDEO SOURCES ENDPOINTS =====

@api_view(['GET'])
def get_consumet_sources(request, anime_slug, episode_number):
    """
    Obtener fuentes de video desde la base de datos
    anime_slug: nombre del anime en formato slug (ej: "one-piece")
    episode_number: número del episodio
    """
    from .models import Anime, Episode
    
    try:
        # Buscar anime y episodio en la base de datos
        anime = Anime.objects.get(anime_slug=anime_slug)
        episode = Episode.objects.get(anime=anime, episode_number=episode_number)
        
        # Verificar si tiene video_url y NO es YouTube
        has_video = episode.video_url and not any(x in episode.video_url for x in ['youtube.com', 'youtu.be'])
        
        if has_video:
            print(f"[VIDEO] ✓ Video encontrado: {anime.title} - Episodio {episode_number}")
            return JsonResponse({
                'sources': [{
                    'url': episode.video_url,
                    'quality': 'default',
                    'isM3U8': episode.video_url.endswith('.m3u8') or 'm3u8' in episode.video_url
                }],
                'headers': {},
                'download': '',
                'source': 'database'
            })
        else:
            if episode.video_url and 'youtube' in episode.video_url:
                print(f"[VIDEO] ⚠️ Ignorando video de YouTube: {anime.title} - Episodio {episode_number}")
            else:
                print(f"[VIDEO] ⚠️ Episodio sin video_url: {anime.title} - Episodio {episode_number}")
            
            return JsonResponse({
                'sources': [{
                    'url': 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
                    'quality': 'default',
                    'isM3U8': True
                }],
                'headers': {},
                'download': '',
                'fallback': True,
                'message': f'El episodio {episode_number} no tiene video MP4 configurado. Mostrando video de demostración.'
            })
            
    except Anime.DoesNotExist:
        print(f"[VIDEO] ✗ No se encontró anime con slug: {anime_slug}")
        return JsonResponse({
            'error': 'Anime no encontrado',
            'message': f'No existe un anime con el slug "{anime_slug}"'
        }, status=404)
        
    except Episode.DoesNotExist:
        print(f"[VIDEO] ✗ No se encontró episodio {episode_number} para {anime_slug}")
        return JsonResponse({
            'error': 'Episodio no encontrado',
            'message': f'El episodio {episode_number} no existe para este anime'
        }, status=404)
        
    except Exception as e:
        print(f"[VIDEO] ✗ Error: {str(e)}")
        return JsonResponse({
            'error': 'Error del servidor',
            'message': str(e)
        }, status=500)
    
    return JsonResponse({
        'sources': [
            {
                'url': 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
                'quality': 'default',
                'isM3U8': True
            }
        ],
        'headers': {
            'Referer': 'https://gogoanime.hu/'
        },
        'download': '',
        'fallback': True,
        'message': 'API de Consumet no disponible. Mostrando video de demostración.',
        'errors': errors,
        'anime_slug': anime_slug,
        'episode': episode_number
    })


@api_view(['GET'])
def search_consumet_anime(request):
    """
    Buscar animes en Consumet/GogoAnime
    """
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)
    
    try:
        url = f"https://api.consumet.org/anime/gogoanime/{query}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data)
        else:
            return JsonResponse({
                'error': f'Consumet API error: {response.status_code}'
            }, status=response.status_code)
            
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Consumet API timeout'}, status=504)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Connection error: {str(e)}'}, status=503)


@api_view(['GET'])
def get_consumet_episodes(request, anime_id):
    """
    Obtener lista de episodios de Consumet para un anime ID de GogoAnime
    anime_id: ID del anime en GogoAnime (ej: "one-piece")
    """
    try:
        url = f"https://api.consumet.org/anime/gogoanime/info/{anime_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Extraer solo los episodios
            episodes = data.get('episodes', [])
            return JsonResponse({
                'episodes': episodes,
                'totalEpisodes': len(episodes)
            })
        else:
            return JsonResponse({
                'error': f'Consumet API error: {response.status_code}'
            }, status=response.status_code)
            
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Consumet API timeout'}, status=504)
    except requests.exceptions.RequestException as e:
       return JsonResponse({'error': f'Connection error: {str(e)}'}, status=503)


# ===== WATCH PROGRESS ENDPOINTS =====

@api_view(['GET'])
def user_progress_list(request):
    """
    Obtener todo el progreso de visualización de los perfiles del usuario actual
    """
    from context.manager.models import Profile
    
    try:
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        # Obtener todos los perfiles del usuario
        user_profiles = Profile.objects.filter(user=request.user)
        
        # Obtener progreso de todos los perfiles del usuario
        progress_list = WatchProgress.objects.filter(profile__in=user_profiles).select_related('anime', 'profile')
        
        data = []
        for p in progress_list:
            try:
                data.append({
                    'anime_id': p.anime.id,
                    'anime_title': p.anime.title,
                    'anime_cover': p.anime.cover_image,
                    'current_episode': p.current_episode,
                    'total_episodes': p.anime.episode_count,
                    'watched': p.watched,
                    'last_watched': p.last_watched.isoformat(),
                    'profile_name': p.profile.name
                })
            except Exception as item_error:
                # Si hay un error con un item específico, continuar con los demás
                print(f"Error processing progress item {p.id}: {str(item_error)}")
                continue
        
        return JsonResponse({'progress': data})
        
    except Exception as e:
        import traceback
        print(f"Error in user_progress_list: {str(e)}")
        print(traceback.format_exc())
        # Devolver lista vacía en lugar de error 500
        return JsonResponse({'progress': []})


@api_view(['GET', 'POST'])
def anime_progress(request, anime_id):
    """
    GET: Obtener progreso de un anime específico para el perfil actual
    POST: Actualizar progreso de un anime para el perfil actual
    """
    from context.manager.models import Profile
    
    try:
        anime = Anime.objects.get(id=anime_id)
    except Anime.DoesNotExist:
        return JsonResponse({'error': 'Anime not found'}, status=404)
    except Exception as e:
        print(f"[PROGRESS] Error buscando anime: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
    # Obtener el perfil actual
    try:
        # Obtener profile_id del header o del body (para POST)
        profile_id = request.headers.get('X-Profile-Id')
        
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                profile_id = data.get('profile_id') or profile_id
            except:
                pass
        
        if profile_id:
            current_profile = Profile.objects.get(id=profile_id, user=request.user)
        else:
            # Si no hay profile_id, usar el primer perfil del usuario
            current_profile = Profile.objects.filter(user=request.user).first()
            
        if not current_profile:
            return JsonResponse({'error': 'No profile found for user'}, status=404)
            
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    except Exception as e:
        print(f"[PROGRESS] Error obteniendo perfil: {e}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)
    
    if request.method == 'GET':
        try:
            progress = WatchProgress.objects.get(profile=current_profile, anime=anime)
            return JsonResponse({
                'anime_id': anime.id,
                'current_episode': progress.current_episode,
                'watched': progress.watched,
                'total_episodes': anime.episode_count or 0,
                'last_watched': progress.last_watched.isoformat() if progress.last_watched else None
            })
        except WatchProgress.DoesNotExist:
            # No hay progreso aún, retornar valores por defecto
            return JsonResponse({
                'anime_id': anime.id,
                'current_episode': 0,
                'watched': False,
                'total_episodes': anime.episode_count or 0,
                'last_watched': None
            })
        except Exception as e:
            print(f"[PROGRESS] Error GET: {e}")
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            current_episode = data.get('current_episode', 0)
            watched = data.get('watched', False)
            
            # Validar que current_episode no exceda el total
            episode_count = anime.episode_count or 0
            if current_episode > episode_count and episode_count > 0:
                current_episode = episode_count
            
            # Si llegó al último episodio, marcar como watched
            if episode_count > 0 and current_episode >= episode_count:
                watched = True
            
            # Actualizar o crear progreso
            progress, created = WatchProgress.objects.update_or_create(
                profile=current_profile,
                anime=anime,
                defaults={
                    'current_episode': current_episode,
                    'watched': watched
                }
            )
            
            return JsonResponse({
                'success': True,
                'anime_id': anime.id,
                'current_episode': progress.current_episode,
                'watched': progress.watched
            })
            
        except json.JSONDecodeError as e:
            print(f"[PROGRESS] JSON Error: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"[PROGRESS] Error POST: {e}")
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)


@api_view(['DELETE'])
def delete_progress(request, anime_id):
    """
    Eliminar progreso de un anime (resetear) para todos los perfiles del usuario
    """
    from context.manager.models import Profile
    
    try:
        anime = Anime.objects.get(id=anime_id)
        # Obtener todos los perfiles del usuario y eliminar progreso para todos
        user_profiles = Profile.objects.filter(user=request.user)
        WatchProgress.objects.filter(profile__in=user_profiles, anime=anime).delete()
        return JsonResponse({'success': True, 'message': 'Progress deleted'})
    except Anime.DoesNotExist:
        return JsonResponse({'error': 'Anime not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ===== ANALYTICS ENDPOINTS =====

@api_view(['GET'])
def analytics_metrics(request):
    """
    Obtener métricas generales de la plataforma
    """
    from django.contrib.auth.models import User
    from context.manager.models import Watchlist, Profile
    from django.db.models import Count, Avg, Q, Sum
    from datetime import timedelta
    from django.utils import timezone
    
    try:
        # Métricas básicas
        total_animes = Anime.objects.count()
        total_episodes = Episode.objects.count()
        total_users = User.objects.count()
        total_profiles = Profile.objects.count()
        total_watchlist_items = Watchlist.objects.count()
        
        # Rating promedio de la plataforma
        avg_rating = Anime.objects.aggregate(Avg('rating'))['rating__avg'] or 0.0
        
        # Distribución por tipo de audio
        audio_distribution = list(Anime.objects.values('audio_type').annotate(count=Count('id')))
        
        # Distribución por géneros (top 10)
        from collections import Counter
        all_genres = []
        try:
            for anime in Anime.objects.all():
                if anime.genre:
                    genres = [g.strip() for g in anime.genre.split(',')]
                    all_genres.extend(genres)
            genre_counter = Counter(all_genres)
            top_genres = [{'name': genre, 'count': count} for genre, count in genre_counter.most_common(10)]
        except Exception:
            top_genres = []
        
        # Top 10 animes más guardados
        try:
            top_saved = list(
                Anime.objects.annotate(
                    saves_count=Count('in_watchlists')
                ).filter(saves_count__gt=0).order_by('-saves_count')[:10].values(
                    'id', 'title', 'cover_image', 'rating', 'saves_count'
                )
            )
        except Exception:
            top_saved = []
        
        # Top 10 animes mejor valorados
        try:
            top_rated = list(
                Anime.objects.filter(rating__gt=0).order_by('-rating')[:10].values(
                    'id', 'title', 'cover_image', 'rating', 'year'
                )
            )
        except Exception:
            top_rated = []
        
        # Distribución por año (últimos 10 años)
        current_year = timezone.now().year
        try:
            years_distribution = list(
                Anime.objects.filter(
                    year__gte=current_year - 10,
                    year__isnull=False
                ).values('year').annotate(count=Count('id')).order_by('year')
            )
        except Exception:
            years_distribution = []
        
        # Métricas de actividad reciente (últimos 30 días)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_watchlist = Watchlist.objects.filter(added_at__gte=thirty_days_ago).count()
        
        # Actividad por día (últimos 30 días)
        daily_activity = []
        for i in range(30):
            day = timezone.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            count = Watchlist.objects.filter(
                added_at__gte=day_start,
                added_at__lte=day_end
            ).count()
            
            daily_activity.append({
                'date': day.strftime('%Y-%m-%d'),
                'count': count
            })
        
        daily_activity.reverse()  # Orden cronológico
        
        # Distribución por tipo de contenido (solo si existe el campo)
        try:
            content_distribution = list(
                Anime.objects.values('content_type').annotate(count=Count('id'))
            )
        except Exception:
            content_distribution = []
        
        # Animes con más episodios
        top_episodes = list(
            Anime.objects.filter(episode_count__gt=0).order_by('-episode_count')[:10].values(
                'id', 'title', 'episode_count', 'cover_image'
            )
        )
        
        return JsonResponse({
            'overview': {
                'total_animes': total_animes,
                'total_episodes': total_episodes,
                'total_users': total_users,
                'total_profiles': total_profiles,
                'total_watchlist_items': total_watchlist_items,
                'average_rating': round(avg_rating, 1),
                'recent_saves_30d': recent_watchlist
            },
            'distributions': {
                'audio_types': audio_distribution,
                'genres': top_genres,
                'years': years_distribution,
                'content_types': content_distribution
            },
            'top_animes': {
                'most_saved': top_saved,
                'best_rated': top_rated,
                'most_episodes': top_episodes
            },
            'activity': {
                'daily_saves': daily_activity
            }
        })
        
    except Exception as e:
        import traceback
        print(f"[ANALYTICS] Error: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

