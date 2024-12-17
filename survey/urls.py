from django.urls import path
from survey import views


app_name = 'survey'  # Добавляем пространство имён
urlpatterns = [
    path('', views.survey_view, name='survey'),  # Главная страница опроса
    path('index/', views.survey_view, name='survey_index'),  # Следующая страница опроса
]
