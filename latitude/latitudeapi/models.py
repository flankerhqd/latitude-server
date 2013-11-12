from django.db import models

# Create your models here.
class Location(models.Model):
    owner = models.ForeignKey('auth.User',related_name="locations")
