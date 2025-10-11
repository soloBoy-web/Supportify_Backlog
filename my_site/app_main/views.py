from django.shortcuts import render
from django.http import HttpResponse




def index(request):
    return render(request=request, template_name="app_main/index.html", context={})

def colours(request):
    return render(request=request, template_name="app_main/colours.html", context={})

def settings(request):
    return HttpResponse("<p> Третий запрос </p>")



def welcome_page(request):
    context = {
        'title': 'Добро пожаловать!',
        'content': 'Это базовый HTML шаблон, который включает в себя все основные элементы веб-страницы.',
        'additional_content': 'Вы можете использовать его как отправную точку для создания своего сайта.'
    }
    return render(request, 'app_main/welcome_page.html', context)


