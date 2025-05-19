# payments/models.py

from django.db import models
from django.conf import settings
from main.models import SubscriptionPlan


class Payment(models.Model):
    # Пользователь, который делает платёж
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # Внешний ID платежа из YooKassa
    yookassa_id = models.CharField(max_length=64, unique=True, verbose_name="YooKassa Payment ID")
    # Сумма и валюта
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    currency = models.CharField(max_length=3, default='RUB', verbose_name="Валюта")
    description = models.CharField(max_length=255, blank=True, verbose_name="Описание")
    test = models.BooleanField(default=False, verbose_name="Тестовый режим")

    # Статус платежа: создан, ожидает подтверждения, успешен, отменён и т.п.
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('waiting_for_capture', 'Ожидает подтверждения'),
        ('succeeded', 'Успешен'),
        ('canceled', 'Отменён'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )

    # Когда YooKassa подтвердил платёж
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата оплаты")
    # Метки времени локального создания/обновления записи
    # Для случая, если платеж можно вернуть
    refundable = models.BooleanField(default=False, verbose_name="Можно вернуть")

    signature = models.CharField(max_length=64, editable=False)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name="Тарифный план"
    )

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return f"{self.user.email} — {self.amount} {self.currency} ({self.status})"
