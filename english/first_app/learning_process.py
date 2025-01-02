import random
from first_app.models import Dictionary, WordsToLearn
from django.shortcuts import render


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
def render_templ(request, data):
    # Находим минимальную стадию среди переданных слов
    min_stage = min(word['stage'] for word in request.session['words'])
    # Находим все слова, находящиеся сейчас на минимальной стадии
    minstage_words = [word for word in request.session['words'] if word['stage'] == min_stage]
    # Берем рандомное слово из minstage_words и находим соответствующий ему индекс в words
    ind = request.session['words'].index(random.choice(minstage_words))
    # Заполняем передаваемые данные с указанием нового слова
    data['word'] = request.session['words'][ind]
    data['id'] = ind
    # Получаем варианты выбора для второго задания
    data['choices'] = get_choices(request, request.session['words'][ind]['word'])
    return render(request, 'first_app/learn_words.html', context=data)