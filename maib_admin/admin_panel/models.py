from django.db import models
from django.contrib.auth.models import User


class Poster(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
    name = models.CharField(max_length = 100, default='')
    ageLim = models.CharField(max_length = 100, default = '+0')
    desc = models.TextField()
    addinfo = models.CharField(max_length = 200, default='')
    addres = models.CharField(max_length = 300, default='')
    date = models.DateField(auto_now_add = True)

class Geo(models.Model):
    name = models.CharField(max_length = 100)
    desc = models.TextField()
    link = models.CharField(max_length = 500)

    def __str__(self):
        return self.name
