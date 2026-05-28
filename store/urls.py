from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("",                  views.store_list,      name="list"),
    path("canjear/<int:item_id>/", views.redeem_view, name="redeem"),
    path("mis-canjes/",       views.my_redemptions,  name="my_redemptions"),
]