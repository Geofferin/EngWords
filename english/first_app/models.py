from django.db import models

class Dictionary(models.Model):
    word = models.CharField(max_length=255)
    translation = models.CharField(max_length=255)
    phrase = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='dictionary/images', blank=True, null=True)
    voice = models.FileField(upload_to='dictionary/audio', blank=True, null=True)
