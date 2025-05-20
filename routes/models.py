from django.contrib.auth.models import AbstractUser
from django.db import models
from Atlas import settings


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Убедитесь, что email уникален
    avatar_image = models.ImageField(upload_to='avatars/', null=True, blank=True,
                                     default='path/to/default/image.jpg')

    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    USERNAME_FIELD = 'email'  # Указываем, что для аутентификации будет использоваться email
    REQUIRED_FIELDS = [
        'username']  # username по-прежнему нужен, но его не будем использовать для входа

    latitude = models.FloatField(null=True, blank=True,
                                 verbose_name="Широта")  # Добавляем поле широты
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота")

    max_routes = models.PositiveIntegerField(default=0, verbose_name="Макс. маршрутов по подписке",
                                             db_default=0)

    def active_subscription(self):
        # возвращает последнюю активную подписку или None
        from django.utils import timezone
        return (
            self.subscriptions
            .filter(end_date__gt=timezone.now())
            .order_by('-end_date')
            .first()
        )

    def remaining_routes(self):
        used = self.route_set.count()
        return max(0, self.max_routes - used)

    def __str__(self):
        return self.email


class WorkingHours(models.Model):
    place = models.ForeignKey(
        'Place',
        on_delete=models.CASCADE,
        related_name='working_hours',
        verbose_name="Заведение"
    )
    day_of_week = models.IntegerField(
        choices=[
            (0, 'Понедельник'),
            (1, 'Вторник'),
            (2, 'Среда'),
            (3, 'Четверг'),
            (4, 'Пятница'),
            (5, 'Суббота'),
            (6, 'Воскресенье')
        ],
        verbose_name="День недели"
    )
    open_time = models.TimeField(verbose_name="Время открытия")
    close_time = models.TimeField(verbose_name="Время закрытия")
    is_closed = models.BooleanField(default=False, verbose_name="Закрыт в этот день")

    class Meta:
        verbose_name = "Рабочее время"
        verbose_name_plural = "Рабочие часы"
        unique_together = ('place', 'day_of_week')  # Уникальность записи для заведения и дня недели

    def __str__(self):
        day = dict(self._meta.get_field('day_of_week').choices).get(self.day_of_week)
        return f"{self.place.name}: {day} - {'Закрыто' if self.is_closed else f'{self.open_time} - {self.close_time}'}"


class Place(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    short_description = models.CharField(max_length=500, verbose_name="Краткое описание")
    full_description = models.TextField(verbose_name="Полное описание")
    address = models.CharField(max_length=150, verbose_name="Адрес")
    location = models.JSONField(verbose_name="Локация", blank=True, null=True)
    image = models.ImageField(upload_to='places_images/', blank=True, null=True,
                              verbose_name="Фото")
    # working_hours = models.ForeignKey(WorkingHours, on_delete=models.CASCADE,
    #                                   verbose_name="Рабочие часы", blank=True, null=True)
    reviews = models.TextField(verbose_name="Отзывы(пока что пустое)", blank=True, null=True)
    category = models.ManyToManyField(Category, verbose_name="Категория")
    slug = models.SlugField(unique=True, verbose_name="URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name="Изменено")
    contacts = models.JSONField(blank=True, null=True, verbose_name="Контакты")
    city = models.CharField(
                max_length = 100,
            verbose_name = "Город",
            default = "Санкт-Петербург",
            help_text = "Город, в котором находится это место")

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = 'Места'

    def __str__(self):
        return self.name


class Route(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()
    days_count = models.BigIntegerField()

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"


class Day(models.Model):
    route_id = models.ForeignKey(Route, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name = "День маршрута"
        verbose_name_plural = "Дни маршрутов"


class RouteCell(models.Model):
    day_id = models.ForeignKey(Day, on_delete=models.CASCADE)
    place_id = models.ForeignKey(Place, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField()

    class Meta:
        verbose_name = "Ячейка маршрута"
        verbose_name_plural = "Ячейки маршрутов"
