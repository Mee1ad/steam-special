from django.urls import path
from . import views

urlpatterns = [
    path('games/', views.steam_games, name='game_list'),
    path('games2/', views.scrape_games, name='game_list2'),
]
