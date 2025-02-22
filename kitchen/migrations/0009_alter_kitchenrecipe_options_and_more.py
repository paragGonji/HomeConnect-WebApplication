# Generated by Django 5.0.7 on 2025-02-02 17:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kitchen', '0008_kitchenrecipe_alter_kitcheninfo_kitchen_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kitchenrecipe',
            options={'ordering': ['-created_at'], 'verbose_name': 'Kitchen Recipe', 'verbose_name_plural': 'Kitchen Recipes'},
        ),
        migrations.AddField(
            model_name='kitchenrecipe',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='kitchenrecipe',
            name='kitchen',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='kitchen.kitcheninfo'),
        ),
        migrations.AlterField(
            model_name='kitchenrecipe',
            name='preparation_time',
            field=models.PositiveIntegerField(default=30),
        ),
        migrations.AlterField(
            model_name='kitchenrecipe',
            name='recipe_rating',
            field=models.FloatField(default=0.0),
        ),
    ]
