import json
import random
from random import choices

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect
import datetime
from first_app.models import Dictionary, WordsToLearn

menu = [
    {'title': 'Словарь', 'url': 'dictionary'},
    {'title': 'Учить слова', 'url': 'learn_words'},
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





# Получаем список слов для задания с выбором правильного перевода из вариантов ответа
def get_choices(request, current_word):
    """
    Так как новые варианты выбора формируются при каждой отрисовке задания,
    то при первом обращении берем 100 рандомных слов из базы и записываем в сессию,
    а затем при каждом новом запросе берем 3 рандомных слова из тех 100
    """
    if 'wrong_words' not in request.session:
        words_data = Dictionary.objects.order_by('?').values('word')[:100]
        wrong_words = [i['word'] for i in words_data]
        request.session['wrong_words'] = wrong_words
        wrong_words = request.session['wrong_words']
    else:
        wrong_words = request.session['wrong_words']

    choices = [
        current_word, random.choices(wrong_words)[0], random.choices(wrong_words)[0], random.choices(wrong_words)[0]
    ]
    # Перемешиваем список
    random.shuffle(choices)
    return choices

def get_new_words(request):
    # Берем первые 5 отсортированных по дате записей из WordsToLearn по id авторизованного пользователя
    db_rq = WordsToLearn.objects.filter(user=request.user.id).order_by('date')[:5]
    # По этим 5 записям, находим соответствующие слова из Dictionary
    words_data = Dictionary.objects.filter(id__in=list(db_rq.values_list('word', flat=True))).values()
    # Преобразуем данные в список словарей
    words = [
        {
            'stage': 0,
            'word': word['word'],
            'translation': word['translation'],
            'db_word_id': word['id'],
            'voice': word['voice'],
            'phrase': word['phrase'],
            'image': word['image'],
        } for word in words_data
    ]
    return words

# Отрисовываем шаблон, выбирая и передавая очередное слово
def render_templ(request, data, words):
    # Находим минимальную стадию среди переданных слов
    min_stage = min(word['stage'] for word in words)
    # Находим все слова, находящиеся сейчас на минимальной стадии
    minstage_words = [word for word in words if word['stage'] == min_stage]
    # Берем рандомное слово из minstage_words и находим соответствующий ему индекс в words
    ind = words.index(random.choice(minstage_words))
    # Заполняем передаваемые данные с указанием нового слова
    data['word'] = words[ind]
    data['id'] = ind
    # Получаем варианты выбора для второго задания
    data['choices'] = get_choices(request, words[ind]['word'])
    return render(request, 'first_app/learn_words.html', context=data)




@login_required(login_url='home')
def learn_words(request):
    data = {
        'title': "learn_words",
        'menu': menu,
    }

    # Сначала получаем список words и записываем в сессию. Затем уже берем список из сессии
    if 'words' not in request.session:
        words = get_new_words(request)
        request.session['words'] = words
    else:
        words = request.session['words']

    if request.method == 'POST':
        word_id = request.POST.get('word_id')
        user_answer = request.POST.get('answer')
        # Если ответ пользователя правильный
        if user_answer == words[int(word_id)]['word']:
            # Увеличиваем стадию изучения слова, чтобы с ним отобразилось следующее задание
            words[int(word_id)]['stage'] += 1
            # Если все слова изучены
            if all(word['stage'] >= 3 for word in words):
                # Создаем список из id изучаемых слов и по нему обращаемся к бд, обновляя даты последнего повторения слов
                list_id = [word['db_word_id'] for word in words]
                WordsToLearn.objects.filter(word__in=list_id).update(date=datetime.datetime.now())
                # Удаляем списки из сессии, чтобы при следующем запуске взять новые слова
                del request.session['words'], request.session['wrong_words']
                # Переводим пользователя на страницу с сообщением об успехе
                return render(request, 'first_app/learn_words_done.html')
            else:
                # Вновь отрисовываем шаблон, передавая новое слово
                request.session['words'] = words
                render_templ(request, data, words)
                messages.success(request, 'Правильный ответ! Переходим к следующему заданию')
        # Для первоначального просмотра слова задан длинный ключ в ответе.
        elif user_answer == 'nezadanie,apervonachalniyprosmotrslovaiperevoda':
            # При его совпадении происходит все то же самое, только без сообщения о правильном ответе
            words[int(word_id)]['stage'] += 1
            request.session['words'] = words
            render_templ(request, data, words)
        # Если ответ неправильный, то предлагается повторить попытку
        else:
            messages.info(request, 'Неправильно. Попробуй еще раз')

    """Выполняется один-первый раз"""
    # Если слов для изучения нет, то в шаблоне будет сообщение об отсутствии слов и кнопка для перехода на add_words
    if len(words) == 0:
        data['word'] = False
        return render(request, 'first_app/learn_words.html', context=data)
    # Если слова есть, то отрисовываем первое слово с первым заданием
    else:
        return render_templ(request, data, words)


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Нема такой страницы:(</h1>Перейти на главную')
