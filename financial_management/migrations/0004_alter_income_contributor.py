# Generated by Django 4.1 on 2023-06-02 04:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financial_management', '0003_remove_income_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='contributor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='financial_management.contributionlevel'),
        ),
    ]