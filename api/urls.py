from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name=''),
    path('games', views.scrape_games, name='game_list'),
]
