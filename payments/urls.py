from django.urls import path, include
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_view, name='payment_view'),  # Создание платежа
    path('call-back', views.payment_cb, name='payment_cb'),  # Получение статуса платежа платежа

]
