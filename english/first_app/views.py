from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
import datetime
from first_app.learning_process import *
from first_app.models import Dictionary, WordsToLearn
from django.shortcuts import render


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


def dictionary_view(request):
    words = Dictionary.objects.all()
    data = {
        'title': "dictionary",
        'menu': menu,
        'words': words
    }
    return render(request, 'first_app/dictionary.html', context=data)


@login_required()
def learn_words(request):
    data = {
        'title': "learn_words",
        'menu': menu,
    }

    # Сначала получаем список words и записываем в сессию. Далее уже работаем с ним
    if 'words' not in request.session:
        request.session['words'] = get_new_words(request)

    if request.method == 'POST':
        word_id = request.POST.get('word_id')
        user_answer = request.POST.get('answer')
        # Если ответ пользователя правильный
        if user_answer == request.session['words'][int(word_id)]['word']:
            # Увеличиваем стадию изучения слова, чтобы с ним отобразилось следующее задание
            request.session['words'][int(word_id)]['stage'] += 1
            # Чтобы новые данные сохранились в сессии, необходимо после изменения указать этот флаг
            request.session.modified = True
            # Если все слова изучены
            if all(word['stage'] >= 3 for word in request.session['words']):
                # Создаем список из id изучаемых слов и по нему обращаемся к бд, обновляя даты последнего повторения слов
                list_id = [word['db_word_id'] for word in request.session['words']]
                WordsToLearn.objects.filter(word__in=list_id).update(date=datetime.datetime.now())
                # Удаляем списки из сессии, чтобы при следующем запуске взять новые слова
                del request.session['words'], request.session['wrong_words']
                # Переводим пользователя на страницу с сообщением об успехе
                return render(request, 'first_app/learn_words_done.html')
            else:
                # Вновь отрисовываем шаблон, передавая новое слово
                render_templ(request, data)
                messages.success(request, 'Правильный ответ! Переходим к следующему заданию')
        # Для первоначального просмотра слова, задан длинный ключ в ответе.
        elif user_answer == 'nezadanie,apervonachalniyprosmotrslovaiperevoda':
            # При его совпадении происходит все то же самое, только без сообщения о правильном ответе
            request.session['words'][int(word_id)]['stage'] += 1
            request.session.modified = True
            render_templ(request, data)
        # Если ответ неправильный, то предлагается повторить попытку
        else:
            messages.info(request, 'Неправильно. Попробуй еще раз')

    """Выполняется только первый раз, дальше уже обрабатываются POST запросы"""
    # Если слов для изучения нет, то в шаблоне будет сообщение об отсутствии слов и кнопка для перехода на add_words
    if len(request.session['words']) == 0:
        data['word'] = False
        return render(request, 'first_app/learn_words.html', context=data)
    # Если слова есть, то отрисовываем первое слово с первым заданием
    else:
        return render_templ(request, data)


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Нема такой страницы:(</h1>Перейти на главную')
