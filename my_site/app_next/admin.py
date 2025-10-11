from django.contrib import admin
from .models import Chat, MessageLog

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'platform', 'is_active')
        }),
        ('Telegram настройки', {
            'fields': ('bot_token', 'chat_id'),
            'description': 'Заполняйте эти поля ТОЛЬКО для Telegram чатов'
        }),
        ('Webhook настройки', {
            'fields': ('webhook_url',),
            'description': 'Заполняйте это поле для Slack/Discord'
        }),
    )

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['chat', 'status', 'created_at', 'user']
    list_filter = ['status', 'chat__platform']
    readonly_fields = ['created_at', 'status_code', 'error_message']