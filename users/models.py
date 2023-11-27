from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

# Create your models here.

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    find_count = models.IntegerField(default=0)


# Holds data for one instance of a Geocache
class Geocache(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default= False)
    password = models.CharField(max_length = 50, default="")
    declined = models.BooleanField(default= False)
    reason = models.CharField(max_length=255, null=True)
    admin = models.ForeignKey(User, on_delete = models.CASCADE,null=True, related_name='admin_geocaches')
    admin_date = models.DateTimeField(null=True)
    cacher = models.ForeignKey(User, on_delete = models.CASCADE)
    find_count = models.IntegerField(default=0)
    cache_date = models.DateTimeField()
    lat = models.DecimalField( max_digits=10, decimal_places=8)
    lng = models.DecimalField( max_digits=11, decimal_places=8)
    description = models.CharField(max_length=500)
    radius = models.IntegerField(null=True)
    password = models.CharField(max_length=12)


    def __str__(self):
        return  "[" + self.name + "]" + "| Submitted By: " + self.cacher.first_name + " " + self.cacher.last_name + "| Found: " + str(self.find_count) + "| Id: " + str(self.id)

# Holds data for one instance of geocache being found
class Find(models.Model):
    finder = models.ForeignKey(User, on_delete= models.CASCADE)
    geocache = models.ForeignKey(Geocache, on_delete= models.CASCADE)
    timestamp = models.DateTimeField()
    hint_count = models.IntegerField(default =0)
    found = models.BooleanField(default=False)

    def __str__(self):
        return self.finder.first_name + " " + self.finder.last_name +  " : " + self.geocache + " : " + str(self.timestamp)


class Comment(models.Model):
    geocache = models.ForeignKey(Geocache, on_delete= models.CASCADE,null=True)
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    text = models.CharField(max_length=255)
    date = models.DateTimeField()

class Hint(models.Model):
    geocache = models.ForeignKey(Geocache, on_delete= models.CASCADE,null=False, related_name="hints")
    text = models.CharField(max_length=150, null=False, blank=False)
    number = models.IntegerField(default=1,null=False)

