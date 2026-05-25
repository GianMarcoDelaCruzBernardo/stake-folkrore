from django.urls import path
from . import views

app_name = 'contests'

urlpatterns = [
    path('', views.contest_list, name='list'),
    path('<slug:slug>/', views.contest_detail, name='detail'),
]
