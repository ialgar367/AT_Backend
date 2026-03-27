from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('context.accounts.api_urls')),
    path('api/manager/', include('context.manager.urls')),
    path('api/backoffice/', include('context.backoffice.urls')),
    path('', include('context.accounts.urls')),
]
