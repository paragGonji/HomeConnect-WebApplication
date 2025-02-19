from django.contrib import admin
from .models import *

# Register other models
admin.site.register(Receipe)
admin.site.register(Department)

# Use Session model without registering it
from django.contrib.sessions.models import Session

# Example: Query sessions (optional logic)
sessions = Session.objects.all()
