from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("app_main.urls")),
    path('next/', include('app_next.urls', namespace='app_next')),



    path('<path:unknown_path>', RedirectView.as_view(url='/next/')),
]
