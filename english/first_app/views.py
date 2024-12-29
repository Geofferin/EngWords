import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect

from first_app.models import Dictionary

menu = [
    {'title': 'Словарь', 'url': 'dictionary'},
    {'title': 'Учить слова', 'url': 'learn_words'},
    {'title': 'О сайте', 'url': 'about'},
    {'title': 'Обратная связь', 'url': 'feedback'},
]


def index(request):
    data = {
        'title': "Main page",
        'menu': menu,
        'important': 'Главная'
    }
    return render(request, 'first_app/index.html', context=data)


@login_required(login_url='home')
def dictionary_view(request):
    words = Dictionary.objects.all()
    data = {
        'title': "dictionary",
        'menu': menu,
        'words': words
    }
    return render(request, 'first_app/dictionary.html', context=data)


@login_required(login_url='home')
def learn_words(request):
    # Получаем случайные 5 слов из базы данных
    words = Dictionary.objects.order_by('?').values('word', 'translation')[:5]  # '?' для случайного порядка

    data = {
        'title': "learn_words",
        'menu': menu,
        'words': json.dumps(list(words))
    }

    return render(request, 'first_app/learn_words.html', context=data)


def about(request):
    data = {
        'title': "about",
        'menu': menu,
    }
    return render(request, 'first_app/about.html', context=data)


@login_required(login_url='home')
def feedback(request):
    data = {
        'title': "feedback",
        'menu': menu,
    }
    return render(request, 'first_app/feedback.html', context=data)


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Нема такой страницы:(</h1>Перейти на главную')