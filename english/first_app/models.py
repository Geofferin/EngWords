from django.db import models
from django.contrib.auth.models import User


class Dictionary(models.Model):
    word = models.CharField(max_length=255)
    translation = models.CharField(max_length=255)
    phrase = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='dictionary/images', blank=True, null=True)
    voice = models.FileField(upload_to='dictionary/audio', blank=True, null=True)
    user = models.ManyToManyField(User, through='WordsToLearn')

# Связующая модель между Dictionary и User
class WordsToLearn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Dictionary, on_delete=models.PROTECT)
    date = models.DateField(null=True)

    class Meta:
        unique_together = ('user', 'word')

    def __str__(self):
        return self.word, self.date
