from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name



class Place(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    short_description = models.CharField(max_length=500, verbose_name="Краткое описание")
    full_description = models.TextField(verbose_name="Полное описание")
    address = models.CharField(max_length=150, verbose_name="Адрес")
    location = models.JSONField(verbose_name="Локация", blank=True, null=True)
    image = models.ImageField(upload_to='places_images/', blank=True, null=True, verbose_name="Фото")
    reviews = models.TextField(verbose_name="Отзывы(пока что пустое)", blank=True, null=True)
    category = models.ManyToManyField(Category, verbose_name="Категория")
    slug = models.SlugField(unique=True, verbose_name="URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(blank=True, null=True, verbose_name="Изменено")
    contacts = models.JSONField(blank=True, null=True, verbose_name="Контакты")

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = 'Места'

    def __str__(self):
        return self.name

class Working_Hours(models.Model):
    place_id = models.ForeignKey(Place, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_close = models.BooleanField()


# class User(AbstractUser):
#     avatar_image = models.ImageField(upload_to='users_avatars/')
#     category = models.ManyToManyField(Category)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField()

class Route(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()
    days_count = models.BigIntegerField()


class Day(models.Model):
    route_id = models.ForeignKey(Route, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()


class Route_Cell(models.Model):
    day_id = models.ForeignKey(Day, on_delete=models.CASCADE)
    place_id = models.ForeignKey(Place, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField()
