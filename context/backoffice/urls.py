from django.urls import path
from . import api_views

urlpatterns = [
    path('animes/', api_views.anime_list, name='anime_list'),
    path('animes/<int:pk>/', api_views.anime_detail, name='anime_detail'),
    path('episodes/', api_views.episode_list, name='episode_list'),
    path('episodes/<int:pk>/', api_views.episode_detail, name='episode_detail'),
]
