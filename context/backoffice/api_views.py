from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Anime, Episode
import json


def admin_only(view_func):
    """Decorador para permitir solo al usuario 'admin'"""
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
        animes = Anime.objects.all()
        data = [{
            'id': anime.id,
            'title': anime.title,
            'year': anime.year,
            'genre': anime.genre,
            'description': anime.description,
            'cover_image': anime.cover_image,
            'background_image': anime.background_image,
            'rating': float(anime.rating),
        } for anime in animes]
        return JsonResponse(data, safe=False)
    
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
        anime_id = request.GET.get('anime_id')
        if anime_id:
            episodes = Episode.objects.filter(anime_id=anime_id)
        else:
            episodes = Episode.objects.all()
        
        data = [{
            'id': episode.id,
            'anime_id': episode.anime.id,
            'episode_number': episode.episode_number,
            'title': episode.title,
            'description': episode.description,
            'duration': episode.duration,
            'video_url': episode.video_url,
            'thumbnail': episode.thumbnail,
        } for episode in episodes]
        return JsonResponse(data, safe=False)
    
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
