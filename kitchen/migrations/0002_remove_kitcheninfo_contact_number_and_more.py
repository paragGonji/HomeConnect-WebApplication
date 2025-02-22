# Generated by Django 5.0.7 on 2025-01-24 17:38

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kitcheninfo',
            name='contact_number',
        ),
        migrations.RemoveField(
            model_name='kitcheninfo',
            name='kitchen_email',
        ),
        migrations.RemoveField(
            model_name='kitcheninfo',
            name='kitchen_is_verified',
        ),
        migrations.RemoveField(
            model_name='kitcheninfo',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='kitcheninfo',
            name='kitchen_password',
            field=models.CharField(default='default_password', max_length=128),
        ),
        migrations.AlterField(
            model_name='kitcheninfo',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='kitcheninfo',
            name='kitchen_address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='kitcheninfo',
            name='kitchen_description',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='kitcheninfo',
            name='kitchen_image',
            field=models.ImageField(default='kitchen/default_image.jpg', upload_to='kitchen'),
        ),
        migrations.AlterField(
            model_name='kitcheninfo',
            name='kitchen_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='kitcheninfo',
            name='kitchen_place',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='kitcheninfo',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
