import hashlib
from django.db import models
from django.conf import settings


class Travel(models.Model):
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    traveler = models.CharField(max_length=50)
    notes = models.TextField()


class SubscriptionPlan(models.Model):
    """
    Планы подписки: сколько маршрутов даёт и на какой срок.
    """
    key = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Автоматически сгенерированный уникальный код плана"
    )
    name = models.CharField(max_length=100,
                            help_text="Человеко-читаемое название (Пакет «Выходные»)")
    routes = models.PositiveIntegerField(help_text="Сколько маршрутов даёт план")
    duration = models.DurationField(help_text="Длительность подписки (например, 30 дней)")
    price = models.DecimalField(max_digits=8, decimal_places=2,
                                help_text="Цена в рублях")
    currency = models.CharField(max_length=3, default='RUB')

    class Meta:
        verbose_name = "Тарифный план"
        verbose_name_plural = "Тарифные планы"

    def __str__(self):
        return f"{self.name} – {self.routes} маршрутов / {self.duration.days} дн. за {self.price} {self.currency}"

    def save(self, *args, **kwargs):
        # Если ключ ещё не установлен — генерируем SHA1-хэш от name и routes
        if not self.key:
            hash_input = f"{self.name}-{self.routes}"
            # берем первые 50 символов hex-представления
            self.key = hashlib.sha1(hash_input.encode('utf-8')).hexdigest()[:50]
        super().save(*args, **kwargs)


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name="Тарифный план"
    )
    purchase_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def is_active(self):
        from django.utils import timezone
        return self.end_date > timezone.now()
