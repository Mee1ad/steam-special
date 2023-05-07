from django.urls import path
from . import views

urlpatterns = [
    path('games', views.scrape_games, name='game_list'),
]
