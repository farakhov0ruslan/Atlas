from django.db import models


class Travel(models.Model):
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    traveler = models.CharField(max_length=50)
    notes = models.TextField()