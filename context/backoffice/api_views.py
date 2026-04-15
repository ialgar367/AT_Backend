from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
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


@admin_only
@require_http_methods(["GET", "POST"])
def anime_list(request):
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
@require_http_methods(["GET", "PUT", "DELETE"])
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


@login_required
@require_http_methods(["GET", "POST"])
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


@login_required
@require_http_methods(["GET", "PUT", "DELETE"])
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

@login_required
@require_http_methods(["GET"])
def public_anime_list(request):
    """Endpoint público para que todos los usuarios vean los animes"""
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
    } for anime in page_obj]
    
    return JsonResponse({
        'results': data,
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }, safe=False)


@login_required
@require_http_methods(["GET"])
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
    })


# ========== JIKAN API INTEGRATION ==========

JIKAN_BASE_URL = "https://api.jikan.moe/v4"

@admin_only
@require_http_methods(["GET"])
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
@require_http_methods(["GET"])
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
@login_required
@require_http_methods(["GET"])
def public_anime_list(request):
    """Endpoint público para listar todos los animes disponibles"""
    # Obtener parámetros de paginación
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Validar page_size
    if page_size > 100:
        page_size = 100
    if page_size < 1:
        page_size = 20
    
    animes = Anime.objects.all().order_by('-created_at')
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

@login_required
@require_http_methods(["GET"])
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
        
        if episode.video_url:
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
                'message': f'El episodio {episode_number} no tiene video configurado. Mostrando video de demostración.'
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


@login_required
@require_http_methods(["GET"])
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


@login_required
@require_http_methods(["GET"])
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

@login_required
@require_http_methods(["GET"])
def user_progress_list(request):
    """
    Obtener todo el progreso de visualización del usuario actual
    """
    try:
        progress_list = WatchProgress.objects.filter(user=request.user).select_related('anime')
        
        data = [{
            'anime_id': p.anime.id,
            'anime_title': p.anime.title,
            'anime_cover': p.anime.cover_image,
            'current_episode': p.current_episode,
            'total_episodes': p.anime.episode_count,
            'watched': p.watched,
            'last_watched': p.last_watched.isoformat()
        } for p in progress_list]
        
        return JsonResponse({'progress': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def anime_progress(request, anime_id):
    """
    GET: Obtener progreso de un anime específico
    POST: Actualizar progreso de un anime
    """
    try:
        anime = Anime.objects.get(id=anime_id)
    except Anime.DoesNotExist:
        return JsonResponse({'error': 'Anime not found'}, status=404)
    
    if request.method == 'GET':
        try:
            progress = WatchProgress.objects.get(user=request.user, anime=anime)
            return JsonResponse({
                'anime_id': anime.id,
                'current_episode': progress.current_episode,
                'watched': progress.watched,
                'total_episodes': anime.episode_count,
                'last_watched': progress.last_watched.isoformat()
            })
        except WatchProgress.DoesNotExist:
            # No hay progreso aún, retornar valores por defecto
            return JsonResponse({
                'anime_id': anime.id,
                'current_episode': 0,
                'watched': False,
                'total_episodes': anime.episode_count,
                'last_watched': None
            })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            current_episode = data.get('current_episode', 0)
            watched = data.get('watched', False)
            
            # Validar que current_episode no exceda el total
            if current_episode > anime.episode_count:
                current_episode = anime.episode_count
            
            # Si llegó al último episodio, marcar como watched
            if current_episode >= anime.episode_count and anime.episode_count > 0:
                watched = True
            
            # Actualizar o crear progreso
            progress, created = WatchProgress.objects.update_or_create(
                user=request.user,
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
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["DELETE"])
def delete_progress(request, anime_id):
    """
    Eliminar progreso de un anime (resetear)
    """
    try:
        anime = Anime.objects.get(id=anime_id)
        WatchProgress.objects.filter(user=request.user, anime=anime).delete()
        return JsonResponse({'success': True, 'message': 'Progress deleted'})
    except Anime.DoesNotExist:
        return JsonResponse({'error': 'Anime not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

