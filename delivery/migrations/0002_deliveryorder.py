# Generated by Django 5.0.7 on 2025-02-08 04:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=100, unique=True)),
                ('customer_name', models.CharField(max_length=255)),
                ('customer_contact', models.CharField(max_length=15)),
                ('customer_address', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('delivery_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='delivery.deliveryperson')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
