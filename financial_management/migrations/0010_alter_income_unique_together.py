# Generated by Django 4.1 on 2023-06-05 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financial_management', '0009_alter_income_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='income',
            unique_together=set(),
        ),
    ]