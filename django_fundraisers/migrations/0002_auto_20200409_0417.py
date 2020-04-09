# Generated by Django 3.0.5 on 2020-04-08 21:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('django_fundraisers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='fundraiser',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='fundraisertransaction',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='created at'),
        ),
    ]
