from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    PLATFORM_CHOICES = [
        ('slack', 'Slack'),
        ('telegram', 'Telegram'),
        ('discord', 'Discord'),
    ]

    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='telegram')
    webhook_url = models.URLField(blank=True, null=True)  # для Slack/Discord
    chat_id = models.CharField(max_length=100, blank=True, null=True)  # для Telegram
    bot_token = models.CharField(max_length=255, blank=True, null=True)  # для Telegram
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.platform})"


class MessageLog(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20)  # success, error
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)