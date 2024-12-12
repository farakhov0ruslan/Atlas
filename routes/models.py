from django.contrib.auth.models import AbstractUser
from django.db import models
from Atlas import settings

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)

class Place(models.Model):
    name = models.CharField(max_length=150)
    short_description = models.CharField(max_length=500)
    full_description = models.TextField()
    address = models.CharField(max_length=150)
    location = models.JSONField()
    image = models.ImageField(upload_to='places_images/')
    reviews = models.TextField()
    category = models.ManyToManyField(Category)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()
    contacts = models.JSONField()

class WorkingHours(models.Model):
    place_id = models.ForeignKey(Place, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_close = models.BooleanField()

class CustomUser(AbstractUser):
    avatar_image = models.ImageField(upload_to='users_avatars/')
    category = models.ManyToManyField(Category)

class Route(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()
    days_count = models.BigIntegerField()

class Day(models.Model):
    route_id = models.ForeignKey(Route, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

class RouteCell(models.Model):
    day_id = models.ForeignKey(Day, on_delete=models.CASCADE)
    place_id = models.ForeignKey(Place, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField()