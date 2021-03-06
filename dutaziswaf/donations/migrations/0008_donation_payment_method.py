# Generated by Django 3.0.5 on 2020-04-09 17:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_cashflow', '0005_auto_20200410_0023'),
        ('donations', '0007_paymentconfirmation'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='donations', to='django_cashflow.Cash', verbose_name='Payment Method'),
        ),
    ]
