# Generated by Django 3.0.5 on 2020-04-08 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_extra_referrals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Balance'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Balance'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='old_balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Old Balance'),
        ),
    ]
