from django.urls import path
from . import api_views

urlpatterns = [
    path('profiles/', api_views.profile_list, name='profile_list'),
    path('profiles/<int:pk>/', api_views.profile_detail, name='profile_detail'),
]
