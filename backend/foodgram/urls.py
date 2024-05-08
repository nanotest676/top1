from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('api/', include('api.urls', namespace='api')),
    path('admin/', admin.site.urls),
    
]
