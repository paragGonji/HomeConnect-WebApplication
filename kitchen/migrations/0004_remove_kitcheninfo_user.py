# Generated by Django 5.0.7 on 2025-01-24 18:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0003_kitcheninfo_kitchen_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kitcheninfo',
            name='user',
        ),
    ]
