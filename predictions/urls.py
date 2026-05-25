from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('make/<slug:slug>/', views.make_prediction, name='make'),
    path('mis-predicciones/', views.my_predictions, name='my_predictions'),
]
