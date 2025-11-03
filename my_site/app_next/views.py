from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, IntegrityError
import logging
from .forms import CustomUserCreationForm
from .models import Chat, MessageLog
import requests
import json


logger = logging.getLogger(__name__)


def handle_exception(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {view_func.__name__}: {str(e)}", exc_info=True)
            messages.error(request, 'Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.')
            return render(request, 'app_next/error.html', {'error_message': str(e)})

    return wrapper


def index(request):
    try:
        active_chats_count = Chat.objects.filter(is_active=True).count()
        total_messages = MessageLog.objects.count()

        context = {
            'active_chats_count': active_chats_count,
            'total_messages': total_messages,
        }
        return render(request, 'app_next/index.html', context)

    except DatabaseError as e:
        logger.error(f"Database error in index: {str(e)}")
        messages.error(request, 'Ошибка базы данных. Пожалуйста, попробуйте позже.')
        return render(request, 'app_next/index.html', {
            'active_chats_count': 0,
            'total_messages': 0
        })
    except Exception as e:
        logger.error(f"Unexpected error in index: {str(e)}")
        messages.error(request, 'Произошла непредвиденная ошибка.')
        return render(request, 'app_next/index.html', {
            'active_chats_count': 0,
            'total_messages': 0
        })


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
        form = CustomUserCreationForm()

    return render(request, 'app_main/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
@handle_exception
def login_view(request):
    if request.user.is_authenticated:
        return redirect('app_next:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Пожалуйста, заполните все поля')
            return render(request, 'app_main/login.html')

        try:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                next_url = request.GET.get('next', 'app_next:welcome')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')

        except Exception as e:
            logger.error(f"Authentication error for user {username}: {str(e)}")
            messages.error(request, 'Ошибка аутентификации. Пожалуйста, попробуйте позже.')

    return render(request, 'app_main/login.html')


@handle_exception
def welcome_view(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Пожалуйста, войдите в систему')
        return redirect('app_next:login')
    return render(request, 'app_main/welcome.html')


@handle_exception
def logout_view(request):
    try:
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы')
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        messages.error(request, 'Ошибка при выходе из системы')

    return redirect('app_main:index')


@require_http_methods(["GET", "POST"])
@handle_exception
def send_message_view(request):
    try:
        chats = Chat.objects.filter(is_active=True)
        results = []

        if request.method == 'POST':
            message_text = request.POST.get('message', '').strip()
            links_text = request.POST.get('links', '').strip()
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

            full_message = format_message_with_links(message_text, links_text)

            for chat_id in selected_chats:
                try:
                    chat = Chat.objects.get(id=chat_id, is_active=True)
                    result = send_to_chat(chat, full_message, request.user)
                    results.append(result)

                    if result['status'] == 'success':
                        messages.success(request, f"Сообщение отправлено в {chat.name}")
                    else:
                        messages.error(request,
                                       f"Ошибка отправки в {chat.name}: {result.get('error', 'Unknown error')}")

                except Chat.DoesNotExist:
                    messages.error(request, f"Чат с ID {chat_id} не найден")
                except Exception as e:
                    logger.error(f"Error sending to chat {chat_id}: {str(e)}")
                    messages.error(request, f"Ошибка при отправке в чат {chat_id}")

    except DatabaseError as e:
        logger.error(f"Database error in send_message_view: {str(e)}")
        messages.error(request, 'Ошибка базы данных. Пожалуйста, попробуйте позже.')
        chats = Chat.objects.none()
        results = []

    return render(request, 'app_next/send_message.html', {
        'chats': chats,
        'results': results
    })


@require_http_methods(["GET", "POST"])
@handle_exception
def send_to_all_chats_view(request):
    try:
        chats = Chat.objects.filter(is_active=True)
        results = []

        if request.method == 'POST':
            message_text = request.POST.get('message', '').strip()
            links_text = request.POST.get('links', '').strip()

            if not message_text and not links_text:
                messages.error(request, 'Введите сообщение или ссылки')
                return render(request, 'app_next/send_to_all.html', {
                    'chats': chats,
                    'results': results
                })
            full_message = format_message_with_links(message_text, links_text)

            for chat in chats:
                try:
                    result = send_to_chat(chat, full_message, request.user)
                    results.append(result)

                    if result['status'] == 'success':
                        messages.success(request, f"Сообщение отправлено в {chat.name}")
                    else:
                        messages.error(request,
                                       f"Ошибка отправки в {chat.name}: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    logger.error(f"Error sending to chat {chat.name}: {str(e)}")
                    messages.error(request, f"Ошибка при отправке в {chat.name}")

    except DatabaseError as e:
        logger.error(f"Database error in send_to_all_chats_view: {str(e)}")
        messages.error(request, 'Ошибка базы данных. Пожалуйста, попробуйте позже.')
        chats = Chat.objects.none()
        results = []

    return render(request, 'app_next/send_to_all.html', {
        'chats': chats,
        'results': results
    })


def format_message_with_links(message_text, links_text):
    try:
        full_message = message_text
        if links_text:
            links = [link.strip() for link in links_text.split('\n') if link.strip()]
            if links:
                links_text_formatted = "\n".join([f"• {link}" for link in links])
                if full_message:
                    full_message += f"\n\nСсылки:\n{links_text_formatted}"
                else:
                    full_message = f"Ссылки:\n{links_text_formatted}"
        return full_message
    except Exception as e:
        logger.error(f"Error formatting message: {str(e)}")
        return message_text


def send_to_chat(chat, message, user=None):
    try:
        if not message or not message.strip():
            raise ValueError("Пустое сообщение")

        if chat.platform == 'telegram':
            return send_to_telegram(chat, message, user)
        else:
            return send_to_webhook(chat, message, user)

    except requests.exceptions.Timeout:
        error_msg = "Таймаут при отправке сообщения"
        logger.error(f"Timeout sending to {chat.name}: {error_msg}")
    except requests.exceptions.ConnectionError:
        error_msg = "Ошибка соединения"
        logger.error(f"Connection error sending to {chat.name}: {error_msg}")
    except requests.exceptions.RequestException as e:
        error_msg = f"Ошибка сети: {str(e)}"
        logger.error(f"Network error sending to {chat.name}: {error_msg}")
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Validation error for {chat.name}: {error_msg}")
    except Exception as e:
        error_msg = f"Неизвестная ошибка: {str(e)}"
        logger.error(f"Unexpected error sending to {chat.name}: {error_msg}")
    try:
        MessageLog.objects.create(
            chat=chat,
            message=message,
            status='error',
            error_message=error_msg,
            user=user
        )
    except Exception as db_error:
        logger.error(f"Failed to log error to database: {str(db_error)}")

    return {
        'chat': chat.name,
        'status': 'error',
        'error': error_msg
    }


def send_to_telegram(chat, message, user=None):
    if not chat.bot_token or not chat.chat_id:
        raise ValueError("Missing bot token or chat ID for Telegram")
    response = None
    try:
        url = f"https://api.telegram.org/bot{chat.bot_token}/sendMessage"
        payload = {
            'chat_id': chat.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()

        response_data = response.json()

        if response_data.get('ok'):
            MessageLog.objects.create(
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
            error_msg = response_data.get('description', 'Unknown Telegram API error')
            raise Exception(f"Telegram API error: {error_msg}")

    except requests.exceptions.Timeout:
        raise Exception("Telegram API timeout (15 seconds)")
    except requests.exceptions.HTTPError as e:
        if response is not None:
            if response.status_code == 404:
                raise Exception("Chat not found or bot token invalid")
            elif response.status_code == 403:
                raise Exception("Bot was blocked by the user")
            elif response.status_code == 400:
                raise Exception("Bad request to Telegram API")
            else:
                raise Exception(f"HTTP error {response.status_code}")
        else:
            raise Exception(f"HTTP error: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Invalid response from Telegram API")
    except Exception as e:
        raise Exception(f"Telegram error: {str(e)}")


def send_to_webhook(chat, message, user=None):
    if not chat.webhook_url:
        raise ValueError("No webhook URL configured")
    response = None
    try:
        payload = {
            'content': message,
            'username': 'News Bot',
            'icon_emoji': ':newspaper:'
        }

        response = requests.post(
            chat.webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        response.raise_for_status()

        MessageLog.objects.create(
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

    except requests.exceptions.Timeout:
        raise Exception("Webhook timeout (15 seconds)")
    except requests.exceptions.HTTPError as e:
        if response is not None:
            if response.status_code == 404:
                raise Exception("Webhook URL not found")
            elif response.status_code == 410:
                raise Exception("Webhook is no longer active")
            elif response.status_code >= 500:
                raise Exception("Webhook server error")
            else:
                raise Exception(f"HTTP error {response.status_code}")
        else:
            raise Exception(f"HTTP error: {str(e)}")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to webhook URL")
    except Exception as e:
        raise Exception(f"Webhook error: {str(e)}")


@handle_exception
def message_history(request):
    try:
        logs = MessageLog.objects.select_related('chat', 'user').all()[:50]
        return render(request, 'app_next/history.html', {'logs': logs})
    except DatabaseError as e:
        logger.error(f"Database error in message_history: {str(e)}")
        messages.error(request, 'Ошибка загрузки истории сообщений')
        return render(request, 'app_next/history.html', {'logs': []})


@require_http_methods(["POST"])
def api_send_message(request):
    try:
        if request.content_type != 'application/json':
            return JsonResponse({'error': 'Content-Type must be application/json'}, status=415)

        data = json.loads(request.body)
        message = data.get('message', '').strip()
        links = data.get('links', [])
        chat_ids = data.get('chat_ids', [])

        if not message and not links:
            return JsonResponse({'error': 'No message or links provided'}, status=400)
        full_message = message
        if links:
            if not isinstance(links, list):
                return JsonResponse({'error': 'Links must be an array'}, status=400)
            links_text = "\n".join([f"• {link}" for link in links if link.strip()])
            full_message += f"\n\nСсылки:\n{links_text}" if full_message else f"Ссылки:\n{links_text}"

        if not full_message.strip():
            return JsonResponse({'error': 'Empty message after processing'}, status=400)

        results = {}
        successful_sends = 0
        try:
            if chat_ids:
                if not isinstance(chat_ids, list):
                    return JsonResponse({'error': 'Chat IDs must be an array'}, status=400)
                chats = Chat.objects.filter(id__in=chat_ids, is_active=True)
            else:
                chats = Chat.objects.filter(is_active=True)

            total_chats = chats.count()

            for chat in chats:
                result = send_to_chat(chat, full_message, request.user)
                results[chat.name] = result
                if result['status'] == 'success':
                    successful_sends += 1
            return JsonResponse({
                'message': f'Message processing completed. Successfully sent to {successful_sends}/{total_chats} chats.',
                'results': results
            })
        except DatabaseError as e:
            logger.error(f"Database error in API: {str(e)}")
            return JsonResponse({'error': 'Database error'}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in API: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)



