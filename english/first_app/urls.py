from django.urls import path
from django.contrib import admin
from .views import *


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', index, name='home'),

    path('dictionary/', dictionary_view, name='dictionary'),
    path('add_words/', add_words, name='add_words'),
    path('about/', about, name='about'),
    path('feedback/', feedback, name='feedback'),
]
