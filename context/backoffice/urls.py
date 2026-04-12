from django.urls import path
from . import api_views

urlpatterns = [
    # Endpoints de administrador (solo admin)
    path('animes/', api_views.anime_list, name='anime_list'),
    path('animes/<int:pk>/', api_views.anime_detail, name='anime_detail'),
    
    # Endpoints de episodios (autenticados)
    path('episodes/', api_views.episode_list, name='episode_list'),
    path('episodes/<int:pk>/', api_views.episode_detail, name='episode_detail'),
    
    # Endpoints públicos (todos los usuarios autenticados)
    path('public/animes/', api_views.public_anime_list, name='public_anime_list'),
    path('public/animes/<int:pk>/', api_views.public_anime_detail, name='public_anime_detail'),
    
    # Jikan API Integration (solo admin)
    path('jikan/search/', api_views.jikan_search, name='jikan_search'),
    path('jikan/anime/<int:mal_id>/', api_views.jikan_anime_detail, name='jikan_anime_detail'),
    
    # Consumet API Integration (usuarios autenticados)
    path('consumet/sources/<str:anime_slug>/<int:episode_number>/', api_views.get_consumet_sources, name='consumet_sources'),
    path('consumet/search/', api_views.search_consumet_anime, name='consumet_search'),
    path('consumet/episodes/<str:anime_id>/', api_views.get_consumet_episodes, name='consumet_episodes'),
    
    # Watch Progress (usuarios autenticados)
    path('progress/', api_views.user_progress_list, name='user_progress_list'),
    path('progress/<int:anime_id>/', api_views.anime_progress, name='anime_progress'),
    path('progress/<int:anime_id>/delete/', api_views.delete_progress, name='delete_progress'),
]
