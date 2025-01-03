from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Receipe)
admin.site.register(StudentID)
admin.site.register(Student)
admin.site.register(Department)