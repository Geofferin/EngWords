from rest_framework import serializers
from .models import Dictionary


class WordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dictionary
        # fields = "__all__"
        fields = ['id', 'word', 'translation', 'phrase', 'image', 'voice']
