from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Receipe(models.Model):
    user = models.ForeignKey(User , on_delete=models.SET_NULL , null = True , blank = True)
    receipe_name = models.CharField(max_length=100)
    receipe_description = models.TextField() 
    receipe_image = models.ImageField(upload_to="receipe")
    receipe_view_count = models.IntegerField(default = 1)
    user_image = models.ImageField(upload_to='user/', null=True, blank=True)


class Department(models.Model):
    department = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.department
    
    class Meta:
        ordering = ['department']

