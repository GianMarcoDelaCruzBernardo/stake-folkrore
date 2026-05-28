from django.urls import path
from . import views

app_name = "predictions"

urlpatterns = [
    path("",                        views.prediction_contest_list, name="list"),
    path("mis-predicciones/",       views.my_predictions,          name="my_predictions"),
    path("<slug:slug>/",            views.vote,                    name="vote"),
    path("<slug:slug>/votar/",      views.submit_vote,             name="submit"),
]