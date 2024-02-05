# players/urls.py

from django.urls import path
from .views import player_profile, get_player_data, get_highest_season_number

urlpatterns = [
    path('player/<str:username>/<str:tag>/', player_profile, name='player_profile'),
    path('get_player_data/', get_player_data, name='get_player_data'),
    path('get_highest_season_number/', get_highest_season_number, name='get_highest_season_number'),
]