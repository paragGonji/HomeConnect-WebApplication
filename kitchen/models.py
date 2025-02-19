from django.db import models
from django.utils.timezone import now

class KitchenInfo(models.Model):
    kitchen_email = models.EmailField(unique=True, null=True)
    kitchen_name = models.CharField(max_length=50)
    kitchen_description = models.CharField(max_length=100)
    kitchen_address = models.TextField()
    kitchen_place = models.CharField(max_length=20)  # Main landmark or main point
    kitchen_image = models.ImageField(upload_to='kitchen/', null=True, blank=True)  # Save under 'media/kitchen/'
    kitchen_password = models.CharField(max_length=128)  # Store hashed password
    created_at = models.DateTimeField(default=now)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # Add this line
    kitchen_earning = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.kitchen_name

    def get_email_field_name(self):
        """Define the email field name explicitly."""
        return 'kitchen_email'  # Return the name of the email field in your model

    def update_last_login(self):
        """Update the last_login field to the current time."""
        self.last_login = now()
        self.save()

    class Meta:
        verbose_name = "Kitchen Information"
        verbose_name_plural = "Kitchen Information"
        ordering = ["-created_at"]

class KitchenDish(models.Model):  # Changed from KitchenRecipe to KitchenDish
    kitchen = models.ForeignKey(KitchenInfo, on_delete=models.CASCADE, related_name="dishes", null=True, blank=True)  # Ensure the foreign key is optional during the creation
    dish_name = models.CharField(max_length=255)  # Name of the dish (formerly recipe_name)
    dish_description = models.TextField()  # Description of the dish (formerly recipe_description)
    dish_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the dish (formerly recipe_price)
    dish_rating = models.FloatField(default=0.0)  # Rating of the dish (formerly recipe_rating)
    preparation_time = models.PositiveIntegerField(default=30)  # Time in minutes to prepare the dish (formerly preparation_time)
    dish_image = models.ImageField(upload_to='dishes/', null=True, blank=True)  # Add Image Field (formerly recipe_image)
    created_at = models.DateTimeField(default=now)  # Timestamp when the dish was created (formerly created_at)
    is_available = models.BooleanField(default=True)  # Whether the dish is available or not (formerly is_available)

    def __str__(self):
        return self.dish_name

    class Meta:
        verbose_name = "Kitchen Dish"
        verbose_name_plural = "Kitchen Dishes"
        ordering = ["-created_at"]
