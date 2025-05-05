from django.urls import path
from routes import views

app_name = 'routes'
urlpatterns = [
    path('', views.route_page, name='route_page'),
    path('start-route/', views.start_route, name='start_route'),
    path('check-route/', views.check_route, name='check_route'),
    path('replace_place/', views.replace_place, name='replace_place'),  # Добавленный URL
]
