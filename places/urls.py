from django.urls import path
from . import views


app_name = 'places'
urlpatterns = [
    path('', views.place_page, name='place_page'),
]