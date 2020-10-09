from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=20)
    age = models.IntegerField()


class Check(models.Model):
    image = models.ImageField()
    texts_list = models.CharField(max_length=12)
    bin = models.IntegerField()
    total = models.TextField()
    data = models.DateField()


