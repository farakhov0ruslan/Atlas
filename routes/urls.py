from django.urls import path
from routes import views


app_name = 'routes'
urlpatterns = [
    path('', views.route_page, name='route_page'),
]
