from django.urls import path
from app_main import views

app_name = 'app_main'

urlpatterns = [
    path('', views.index, name="index"),
    path('price/', views.price, name="price"),
    path('settings/', views.settings, name="settings"),
    path('welcome_page/', views.welcome_page, name="welcome_page"),
    path('contact/', views.contact, name="contact"),
]
