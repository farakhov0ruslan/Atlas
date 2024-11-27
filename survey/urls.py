from django.urls import path
from survey import views


app_name = 'survey'
urlpatterns = [
    path('', views.survey_index, name='survey_index'),
    path('second', views.survey_second, name='survey_second'),
]
