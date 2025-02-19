from django.db import models
from django.utils.timezone import now


# Create your models here.
class DeliveryPerson(models.Model):
    delivery_email = models.EmailField(unique=True, null=True)
    delivery_name = models.CharField(max_length=50)
    delivery_contact = models.CharField(max_length=15, unique=True)  # Renamed from phone_no
    delivery_address = models.TextField()
    delivery_area = models.CharField(max_length=50)  # Main landmark or service area
    delivery_image = models.ImageField(upload_to='delivery/', null=True, blank=True)  # Save under 'media/delivery/'
    delivery_password = models.CharField(max_length=128)  # Store hashed password
    delivery_registered_at = models.DateTimeField(default=now)  # Renamed from created_at
    delivery_last_login = models.DateTimeField(null=True, blank=True)  # Renamed from last_login
    delivery_status = models.BooleanField(default=False)  # Renamed from is_active
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field

    def __str__(self):
        return self.delivery_name

    def get_email_field_name(self):
        """Define the email field name explicitly."""
        return 'delivery_email'  # Return the name of the email field in your model

    def update_delivery_last_login(self):
        """Update the last_login field to the current time."""
        self.delivery_last_login = now()
        self.save()

    class Meta:
        verbose_name = "Delivery Person"
        verbose_name_plural = "Delivery Persons"
        ordering = ["-delivery_registered_at"]

class DeliveryOrder(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    customer_name = models.CharField(max_length=255)
    customer_contact = models.CharField(max_length=15)
    customer_address = models.TextField()
    items = models.JSONField(default=dict)  # Store cart items as JSON
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Store total price
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('assigned', 'Assigned'),
            ('in_progress', 'In Progress'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"

    class Meta:
        ordering = ["-created_at"]