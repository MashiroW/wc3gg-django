# myapp/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('books/', book_list, name='book_list'),
    path('leaderboards/', leaderboards, name='leaderboards'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('api/leaderboards/', get_filtered_leaderboard, name='get_filtered_leaderboard'),
    path('get_total_count/', get_total_count, name='get_total_count'),
    path('get_battle_tags/', get_battle_tags, name='get_battle_tags'),
    path('get_distribution/', get_distribution, name='get_distribution'),
]
