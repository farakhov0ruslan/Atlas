from django.urls import path
from . import views

app_name = 'places'
urlpatterns = [
    path('', views.place_list, name='place_page'),
    path('category/<slug:category_slug>/', views.place_list, name='place_by_category'),
]