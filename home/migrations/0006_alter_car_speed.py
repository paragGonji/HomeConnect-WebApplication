# Generated by Django 5.0.7 on 2024-08-14 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_rename_product_car'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='speed',
            field=models.IntegerField(default=50),
        ),
    ]
