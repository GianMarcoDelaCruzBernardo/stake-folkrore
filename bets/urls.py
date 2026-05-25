from django.urls import path
from . import views

app_name = "bets"

urlpatterns = [
    path("",                         views.bet_contest_list, name="list"),
    path("mis-tickets/",             views.my_bets,          name="my_bets"),
    path("apostar/<int:option_id>/", views.place_bet_view,   name="place"),
    path("<slug:slug>/",             views.bet_lobby,        name="lobby"),
]
