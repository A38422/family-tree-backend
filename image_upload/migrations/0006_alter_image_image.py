# Generated by Django 4.1 on 2023-05-18 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_upload', '0005_alter_image_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='media/images'),
        ),
    ]
