from django.urls import path
from . import api_views

urlpatterns = [
    path('profiles/', api_views.profile_list, name='profile_list'),
    path('profiles/<int:pk>/', api_views.profile_detail, name='profile_detail'),
    path('watchlist/', api_views.watchlist, name='watchlist'),
    path('watchlist/remove/<int:anime_id>/', api_views.watchlist_remove, name='watchlist_remove'),
]
