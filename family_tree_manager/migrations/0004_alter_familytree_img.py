# Generated by Django 4.1 on 2023-05-16 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('family_tree_manager', '0003_alter_familytree_img_alter_familytree_pids_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familytree',
            name='img',
            field=models.TextField(blank=True, null=True),
        ),
    ]