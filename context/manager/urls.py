from django.urls import path
from . import api_views

urlpatterns = [
    path('profiles/', api_views.profile_list, name='profile_list'),
    path('profiles/<int:pk>/', api_views.profile_detail, name='profile_detail'),
    
    # Watchlist endpoints
    path('watchlist/', api_views.watchlist_list, name='watchlist_list'),
    path('watchlist/add/', api_views.watchlist_add, name='watchlist_add'),
    path('watchlist/remove/<int:anime_id>/', api_views.watchlist_remove, name='watchlist_remove'),
    path('watchlist/check/<int:anime_id>/', api_views.watchlist_check, name='watchlist_check'),
]
