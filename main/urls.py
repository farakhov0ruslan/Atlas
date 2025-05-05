from django.urls import path, include
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('register/', views.register, name='register'),  # Регистрация
    path('profile/', views.profile, name='profile'),  # Профиль пользователя
    path('logout/', views.custom_logout, name='logout'),
    path('login/', views.login_view, name='login'),
    path('save-location-session/', views.save_location_to_session, name="save_location_session"),
    path('save-location-db/', views.save_location_to_db, name="save_location_db"),
    path('get-location/', views.get_user_location, name="get_user_location"),
    path('oferta/', views.offer, name='offer'),
    path('prices/', views.prices, name='prices'),
]
