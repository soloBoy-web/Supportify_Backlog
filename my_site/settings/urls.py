from django.contrib import admin
from django.urls import path, include




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("app_main.urls")),
    path('next/', include('app_next.urls', namespace='app_next')),
]
