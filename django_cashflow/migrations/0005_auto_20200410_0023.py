# Generated by Django 3.0.5 on 2020-04-09 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_cashflow', '0004_auto_20200407_1913'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mutation',
            options={'ordering': ['-created_at'], 'verbose_name': 'Mutation', 'verbose_name_plural': 'Mutations'},
        ),
    ]
