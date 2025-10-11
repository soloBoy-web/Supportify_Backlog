from django.urls import path
from app_next import views


app_name = 'app_next'

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('welcome/', views.welcome_view, name='welcome'),
    path('send/', views.send_message_view, name='send_message'),
    path('send-all/', views.send_to_all_chats_view, name='send_to_all'),
    path('history/', views.message_history, name='message_history'),
    path('api/send/', views.api_send_message, name='api_send_message'),
]
