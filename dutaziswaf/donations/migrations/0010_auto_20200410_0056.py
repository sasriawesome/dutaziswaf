# Generated by Django 3.0.5 on 2020-04-09 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0009_auto_20200410_0055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentconfirmation',
            name='note',
            field=models.TextField(blank=True, help_text='Need help? please tell us.', max_length=500, null=True, verbose_name='Note'),
        ),
    ]
