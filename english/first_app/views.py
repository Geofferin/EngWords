import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect
import datetime
from first_app.models import Dictionary, WordsToLearn

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
    # Берем первые 5 отсортированных по дате записей из WordsToLearn по id авторизованного пользователя
    words_to_learn = WordsToLearn.objects.filter(user=request.user.id).order_by('date')[:5]
    # По этим 5 записям, находим соответствующие слова из Dictionary
    # Сейчас берутся только два значения - слово и перевод. При добавлении произношения, нужно добавить его передачу и сюда
    words = Dictionary.objects.filter(id__in=list(words_to_learn.values_list('word', flat=True))).values('word', 'translation')


    data = {
        'title': "learn_words",
        'menu': menu,
        'words': json.dumps(list(words))
    }

    # У выбранных 5 слов обновляется дата. Таким образом они перемещаются в конец очереди на обучение
    WordsToLearn.objects.filter(id__in=list(words_to_learn.values_list('id', flat=True))).update(date=datetime.datetime.now())

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