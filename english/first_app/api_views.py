import datetime
from django.core.serializers import serialize
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Dictionary, WordsToLearn
from .serializers import WordsSerializer


class LearnView(APIView):
    permission_classes = [IsAuthenticated]

    # Возвращаем необходимые для изучения слова и 100 рандомных слов
    def get(self, request):
        # Получаем 5 записей из WordsToLearn, сортируя по дате
        words_to_learn = WordsToLearn.objects.filter(user=request.user).order_by('date')[:5]
        # Извлекаем объекты слов из words_to_learn
        dictionary_words = [i.word for i in words_to_learn]
        # Преобразуем список объектов (dictionary_words) в JSON, с помощью сериализатора
        serializer = WordsSerializer(dictionary_words, many=True)

        # Берем еще 100 рандомных слов для упражнения с выбором перевода
        added_word_ids = [word.id for word in dictionary_words]
        # exclude исключает переданные слова. Это исключает шанс того, что среди этих слов окажутся правильные
        wrong_words = list(Dictionary.objects.exclude(id__in=added_word_ids).order_by('?').values_list('word', flat=True)[:100])

        # Объединяем данные в одном словаре
        response_body = {"added_words": serializer.data, "wrong_words": wrong_words}
        return Response(response_body, status=status.HTTP_200_OK)

    # Просто повторно берем те же 5 слов и обновляем у них дату
    def post(self, request):
        words_to_learn = WordsToLearn.objects.filter(user=request.user).order_by('date')[:5]
        words_id = [i.word.id for i in words_to_learn]
        WordsToLearn.objects.filter(user=request.user, word_id__in=words_id).update(date=datetime.datetime.now())
        return Response({'message': 'Date updated successfully'}, status=status.HTTP_200_OK)


class AddWordsView(APIView):
    permission_classes = [IsAuthenticated]

    # Получаем список всех слов
    def get(self, request):
        words_to_add = Dictionary.objects.all()
        serializer = WordsSerializer(words_to_add, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Добавляем выбранные слова в список на изучение
    def post(self, request):
        """ Получаем данные вида: {"id": [57, 210, 7]} """
        words_id = request.data.get('id')

        if not words_id:
            return Response({'error': 'id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Находим слова в Dictionary по переданным id
        words = Dictionary.objects.filter(id__in=words_id)
        # Проверяем, найдено ли хоть одно слово по переданным id
        if len(words) < 1:
            return Response({'error': 'These words were not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Формируем список записей, который затем передается при пакетной записи данных в таблицу (bulk_create)
            words_to_learn_list = [WordsToLearn(user=request.user, word=word, date=datetime.datetime.now()) for word in words]
            WordsToLearn.objects.bulk_create(words_to_learn_list)
            return Response({'message': 'Words added'}, status=status.HTTP_200_OK)


class MyWordsView(APIView):
    permission_classes = [IsAuthenticated]

    # Получение списка слов, добавленных на изучение
    def get(self, request):
        words_to_learn = WordsToLearn.objects.filter(user=request.user).order_by('date')
        dictionary_words = [item.word for item in words_to_learn]
        serializer = WordsSerializer(dictionary_words, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Удаление слов из списка на изучение
    def post(self, request):
        """ Получаем данные вида: {"id": [57, 210, 7]} """
        words_id = request.data.get('id')

        if not words_id:
            return Response({'error': 'id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Находим соответствующие записи. Все не найденные id будут проигнорированны, если есть хоть один существующий id
        existing_words = WordsToLearn.objects.filter(word_id__in=words_id, user=request.user)
        if len(existing_words) < 1:
            return Response({'error': 'These words were not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            existing_words.delete()
            return Response({'message': 'Words deleted'}, status=status.HTTP_200_OK)
