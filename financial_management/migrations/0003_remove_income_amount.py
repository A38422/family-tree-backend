# Generated by Django 4.1 on 2023-06-02 03:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financial_management', '0002_income_member'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='income',
            name='amount',
        ),
    ]