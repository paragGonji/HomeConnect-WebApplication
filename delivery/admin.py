from django.contrib import admin
from .models import *

# Use Session model without registering it
from django.contrib.sessions.models import Session

# Example: Fetch sessions (optional logic)
sessions = Session.objects.all()
admin.site.register(DeliveryPerson)
admin.site.register(DeliveryOrder)

# Register other models
# admin.site.register(SomeOtherModel)  # Example if you have other models to register
