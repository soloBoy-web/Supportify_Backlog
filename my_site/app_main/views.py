from django.shortcuts import render
from django.contrib.auth.decorators import login_required



def index(request):
    return render(request=request, template_name="app_main/index.html", context={})


def price(request):
    return render(request=request, template_name="app_main/price.html", context={})


@login_required
def settings(request):
    context = {
        'user': request.user,
    }
    return render(request, 'app_main/user_settings.html', context)


def contact(request):
    return render(request=request, template_name="app_main/contact.html", context={})


def welcome_page(request):
    context = {
        'title': 'Отправляйте сообщения легко и быстро! 🚀',
        'content': [
            'Всего 3 простых шага к результату:',
            '📋 Выберите чаты и каналы из доступного списка',
            '✍️ Напишите текст или добавьте ссылку',
            '📤 Нажмите кнопку "Отправить"'
        ],
        'additional_content': 'И наблюдайте, как ваше сообщение моментально появляется во всех выбранных местах! ✨'
    }
    return render(request=request, template_name='app_main/welcome_page.html', context=context)
