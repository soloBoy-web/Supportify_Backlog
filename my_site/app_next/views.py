from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CustomUserCreationForm
from .models import Chat, MessageLog
import requests
import json




def index(request):
    """Главная страница"""
    active_chats_count = Chat.objects.filter(is_active=True).count()
    total_messages = MessageLog.objects.count()

    context = {
        'active_chats_count': active_chats_count,
        'total_messages': total_messages,
    }
    return render(request, 'app_next/index.html', context)



@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('app_next:welcome')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Аккаунт создан! Добро пожаловать, {user.username}!')
            return redirect('app_next:welcome')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'app_main/register.html', {'form': form})  # Исправил на app_main

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('app_next:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Пожалуйста, заполните все поля')
            return render(request, 'app_main/login.html')  # Исправил на app_main

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'app_next:welcome')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
            return render(request, 'app_main/login.html')  # Исправил на app_main

    return render(request, 'app_main/login.html')  # Исправил на app_main

def welcome_view(request):
    """Страница приветствия после регистрации"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Пожалуйста, войдите в систему')
        return redirect('app_next:login')
    return render(request, 'app_main/welcome.html')  # Исправил на app_main

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('app_main:index')



def send_message_view(request):
    """Страница отправки сообщений"""
    chats = Chat.objects.filter(is_active=True)
    results = []

    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        links_text = request.POST.get('links', '')
        selected_chats = request.POST.getlist('chats')

        if not message_text and not links_text:
            messages.error(request, 'Введите сообщение или ссылки')
            return render(request, 'app_next/send_message.html', {
                'chats': chats,
                'results': results
            })

        if not selected_chats:
            messages.error(request, 'Выберите хотя бы один чат')
            return render(request, 'app_next/send_message.html', {
                'chats': chats,
                'results': results
            })

        # Формируем полное сообщение
        full_message = message_text
        if links_text:
            links = [link.strip() for link in links_text.split('\n') if link.strip()]
            if links:
                links_text_formatted = "\n".join([f"• {link}" for link in links])
                if full_message:
                    full_message += f"\n\nСсылки:\n{links_text_formatted}"
                else:
                    full_message = f"Ссылки:\n{links_text_formatted}"

        # Отправляем в выбранные чаты
        for chat_id in selected_chats:
            try:
                chat = Chat.objects.get(id=chat_id, is_active=True)
                result = send_to_chat(chat, full_message, request.user)
                results.append(result)

                if result['status'] == 'success':
                    messages.success(request, f"Сообщение отправлено в {chat.name}")
                else:
                    messages.error(request, f"Ошибка отправки в {chat.name}: {result.get('error', 'Unknown error')}")

            except Chat.DoesNotExist:
                messages.error(request, f"Чат с ID {chat_id} не найден")

    return render(request, 'app_next/send_message.html', {
        'chats': chats,
        'results': results
    })

def send_to_all_chats_view(request):
    """Отправка сообщения во все активные чаты"""
    chats = Chat.objects.filter(is_active=True)
    results = []

    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        links_text = request.POST.get('links', '')

        if not message_text and not links_text:
            messages.error(request, 'Введите сообщение или ссылки')
            return render(request, 'app_next/send_to_all.html', {
                'chats': chats,
                'results': results
            })

        # Формируем полное сообщение
        full_message = message_text
        if links_text:
            links = [link.strip() for link in links_text.split('\n') if link.strip()]
            if links:
                links_text_formatted = "\n".join([f"• {link}" for link in links])
                if full_message:
                    full_message += f"\n\nСсылки:\n{links_text_formatted}"
                else:
                    full_message = f"Ссылки:\n{links_text_formatted}"

        # Отправляем во все активные чаты
        for chat in chats:
            result = send_to_chat(chat, full_message, request.user)
            results.append(result)

            if result['status'] == 'success':
                messages.success(request, f"Сообщение отправлено в {chat.name}")
            else:
                messages.error(request, f"Ошибка отправки в {chat.name}: {result.get('error', 'Unknown error')}")

    return render(request, 'app_next/send_to_all.html', {
        'chats': chats,
        'results': results
    })


def send_to_chat(chat, message, user=None):
    """Вспомогательная функция для отправки сообщения в конкретный чат"""
    try:
        if chat.platform == 'telegram':
            return send_to_telegram(chat, message, user)
        else:
            return send_to_webhook(chat, message, user)

    except Exception as e:
        log_entry = MessageLog.objects.create(
            chat=chat,
            message=message,
            status='error',
            error_message=str(e),
            user=user
        )
        return {
            'chat': chat.name,
            'status': 'error',
            'error': str(e)
        }


def send_to_telegram(chat, message, user=None):
    """Отправка сообщения в Telegram"""
    if not chat.bot_token or not chat.chat_id:
        return {
            'chat': chat.name,
            'status': 'error',
            'error': 'Missing bot token or chat ID'
        }

    url = f"https://api.telegram.org/bot{chat.bot_token}/sendMessage"

    payload = {
        'chat_id': chat.chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    response = requests.post(
        url,
        json=payload,
        timeout=10
    )

    response_data = response.json()

    if response.status_code == 200 and response_data.get('ok'):
        log_entry = MessageLog.objects.create(
            chat=chat,
            message=message,
            status='success',
            status_code=response.status_code,
            user=user
        )
        return {
            'chat': chat.name,
            'status': 'success',
            'status_code': response.status_code
        }
    else:
        error_msg = response_data.get('description', 'Unknown error')
        log_entry = MessageLog.objects.create(
            chat=chat,
            message=message,
            status='error',
            status_code=response.status_code,
            error_message=error_msg,
            user=user
        )
        return {
            'chat': chat.name,
            'status': 'error',
            'status_code': response.status_code,
            'error': error_msg
        }


def send_to_webhook(chat, message, user=None):
    """Отправка через вебхук (для Slack/Discord)"""
    if not chat.webhook_url:
        return {
            'chat': chat.name,
            'status': 'error',
            'error': 'No webhook URL configured'
        }

    payload = {
        'text': message,
        'username': 'News Bot',
        'icon_emoji': ':newspaper:'
    }

    response = requests.post(
        chat.webhook_url,
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )

    if response.status_code == 200:
        log_entry = MessageLog.objects.create(
            chat=chat,
            message=message,
            status='success',
            status_code=response.status_code,
            user=user
        )
        return {
            'chat': chat.name,
            'status': 'success',
            'status_code': response.status_code
        }
    else:
        log_entry = MessageLog.objects.create(
            chat=chat,
            message=message,
            status='error',
            status_code=response.status_code,
            error_message=f"HTTP {response.status_code}: {response.text}",
            user=user
        )
        return {
            'chat': chat.name,
            'status': 'error',
            'status_code': response.status_code,
            'error': response.text
        }


# Остальные view функции остаются как были
def send_message(request):
    """Страница отправки сообщений"""
    chats = Chat.objects.filter(is_active=True)
    results = []

    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        links_text = request.POST.get('links', '')
        selected_chats = request.POST.getlist('chats')

        if not message_text and not links_text:
            messages.error(request, 'Введите сообщение или ссылки')
            return render(request, 'app_next/send_message.html', {
                'chats': chats,
                'results': results
            })

        if not selected_chats:
            messages.error(request, 'Выберите хотя бы один чат')
            return render(request, 'app_next/send_message.html', {
                'chats': chats,
                'results': results
            })

        # Формируем полное сообщение
        full_message = message_text
        if links_text:
            links = [link.strip() for link in links_text.split('\n') if link.strip()]
            if links:
                links_text_formatted = "\n".join([f"• {link}" for link in links])
                if full_message:
                    full_message += f"\n\nСсылки:\n{links_text_formatted}"
                else:
                    full_message = f"Ссылки:\n{links_text_formatted}"

        # Отправляем в выбранные чаты
        for chat_id in selected_chats:
            try:
                chat = Chat.objects.get(id=chat_id, is_active=True)
                result = send_to_chat(chat, full_message, request.user)
                results.append(result)

                if result['status'] == 'success':
                    messages.success(request, f"Сообщение отправлено в {chat.name}")
                else:
                    messages.error(request, f"Ошибка отправки в {chat.name}: {result.get('error', 'Unknown error')}")

            except Chat.DoesNotExist:
                messages.error(request, f"Чат с ID {chat_id} не найден")

    return render(request, 'app_next/send_message.html', {
        'chats': chats,
        'results': results
    })


def send_to_all(request):
    """Отправка сообщения во все активные чаты"""
    chats = Chat.objects.filter(is_active=True)
    results = []

    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        links_text = request.POST.get('links', '')

        if not message_text and not links_text:
            messages.error(request, 'Введите сообщение или ссылки')
            return render(request, 'app_next/send_to_all.html', {
                'chats': chats,
                'results': results
            })

        # Формируем полное сообщение
        full_message = message_text
        if links_text:
            links = [link.strip() for link in links_text.split('\n') if link.strip()]
            if links:
                links_text_formatted = "\n".join([f"• {link}" for link in links])
                if full_message:
                    full_message += f"\n\nСсылки:\n{links_text_formatted}"
                else:
                    full_message = f"Ссылки:\n{links_text_formatted}"

        # Отправляем во все активные чаты
        for chat in chats:
            result = send_to_chat(chat, full_message, request.user)
            results.append(result)

            if result['status'] == 'success':
                messages.success(request, f"Сообщение отправлено в {chat.name}")
            else:
                messages.error(request, f"Ошибка отправки в {chat.name}: {result.get('error', 'Unknown error')}")

    return render(request, 'app_next/send_to_all.html', {
        'chats': chats,
        'results': results
    })

def message_history(request):
    """История отправленных сообщений"""
    logs = MessageLog.objects.select_related('chat', 'user').all()[:50]
    return render(request, 'app_next/history.html', {'logs': logs})


def api_send_message(request):
    """API endpoint для отправки сообщений"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            links = data.get('links', [])
            chat_ids = data.get('chat_ids', [])

            if not message and not links:
                return JsonResponse({'error': 'No message or links provided'}, status=400)

            # Формируем полное сообщение
            full_message = message
            if links:
                links_text = "\n".join([f"• {link}" for link in links])
                full_message += f"\n\nСсылки:\n{links_text}"

            results = {}

            if chat_ids:
                chats = Chat.objects.filter(id__in=chat_ids, is_active=True)
            else:
                chats = Chat.objects.filter(is_active=True)

            for chat in chats:
                result = send_to_chat(chat, full_message, request.user)
                results[chat.name] = result

            return JsonResponse({
                'message': 'Message processing completed',
                'results': results
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)