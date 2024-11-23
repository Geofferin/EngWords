from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from first_app.models import Dictionary

menu = [
    {'title': 'На главную', 'url': 'home'},
    {'title': 'Словарь', 'url': 'dictionary'},
    {'title': 'Добавить слова', 'url': 'add_words'},
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

def add_words(request):
    data = {
        'title': "add_words",
        'menu': menu,
    }
    return render(request, 'first_app/add_words.html', context=data)

def about(request):
    data = {
        'title': "about",
        'menu': menu,
    }
    return render(request, 'first_app/about.html', context=data)

def feedback(request):
    data = {
        'title': "feedback",
        'menu': menu,
    }
    return render(request, 'first_app/feedback.html', context=data)

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Нема такой страницы:(</h1>Перейти на главную')