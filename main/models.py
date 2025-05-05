from django.db import models
from django.conf import settings

class Travel(models.Model):
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    traveler = models.CharField(max_length=50)
    notes = models.TextField()

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('выходные', 'Выходные'),
        ('отпуск', 'Отпуск'),
        ('каникулы', 'Каникулы'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    purchase_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def is_active(self):
        from django.utils import timezone
        return self.end_date > timezone.now()