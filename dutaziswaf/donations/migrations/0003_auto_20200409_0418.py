# Generated by Django 3.0.5 on 2020-04-08 21:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0002_auto_20200409_0417'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donation',
            old_name='mustahiq',
            new_name='fundraiser',
        ),
    ]
