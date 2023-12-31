# Generated by Django 4.1 on 2023-05-15 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyTree',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('relationship', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('img', models.CharField(max_length=255)),
                ('bdate', models.DateField()),
                ('ddate', models.DateField(blank=True, null=True)),
                ('fid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='spouses', to='family_tree_manager.familytree')),
                ('mid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='family_tree_manager.familytree')),
                ('pids', models.ManyToManyField(blank=True, related_name='parents', to='family_tree_manager.familytree')),
            ],
        ),
    ]
