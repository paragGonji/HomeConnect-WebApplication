# Generated by Django 5.0.7 on 2024-08-14 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_remove_student_file_remove_student_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='Car',
            new_name='Car_name',
        ),
        migrations.AddField(
            model_name='product',
            name='speed',
            field=models.ImageField(default=50, upload_to=''),
        ),
    ]
