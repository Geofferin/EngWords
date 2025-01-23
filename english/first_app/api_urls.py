from django.urls import path
from django.contrib import admin
from users.urls import app_name
from .api_views import *

app_name = 'api'

urlpatterns = [
    path('v1/learn/', LearnView.as_view(), name='api_learn'),
    path('v1/add_words/', AddWordsView.as_view(), name='api_add_words'),
    path('v1/my_words/', MyWordsView.as_view(), name='api_my_words'),
]