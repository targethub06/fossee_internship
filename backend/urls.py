from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.core_urls if hasattr(admin.site, 'core_urls') else admin.site.urls),
    path('api/', include('api.urls')),
]
