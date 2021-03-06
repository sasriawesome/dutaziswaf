# Generated by Django 3.0.5 on 2020-04-07 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('django_cashflow', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mutation',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='mutation',
            name='object_id',
        ),
        migrations.AddField(
            model_name='checkin',
            name='content_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'model__in': ['donation']}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType', verbose_name='reference type'),
        ),
        migrations.AddField(
            model_name='checkin',
            name='object_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='reference id'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='content_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'model__in': ['withdraw']}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType', verbose_name='reference type'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='object_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='reference id'),
        ),
    ]
