from django.contrib import admin
from django.urls import path, include
from backend.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path("api/", include("api.urls")),
    path("api-auth/", include("rest_framework.urls")),
]                            
