from django.db import models

# Create your models here.


class student(models.Model):
    name = models.CharField(max_length=20)
    age = models.IntegerField()
    email = models.EmailField(null=True , blank=True)
    address = models.TextField(null=True, blank=True)
    


class Car(models.Model):
    Car_name = models.CharField(max_length=10)
    speed = models.IntegerField(default=50)


    def __str__(self) -> str:
        return self.Car_name