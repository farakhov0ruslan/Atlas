from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('register/', views.register, name='register'),  # Регистрация
    path('profile/', views.profile, name='profile'),  # Профиль пользователя
    path('logout/', views.custom_logout, name='logout'),
    path('login/', views.login_view, name='login'),
]
