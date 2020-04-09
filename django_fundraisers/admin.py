from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.apps import apps

from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from mptt.admin import MPTTModelAdmin

from .models import (
    Fundraiser, FundraiserTransaction
)


@admin.register(Fundraiser)
class FundraiserAdmin(admin.ModelAdmin):
    list_display = ['inner_id', 'name', 'founder', 'balance']


@admin.register(FundraiserTransaction)
class FundraiserTransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_filter = ['created_at', 'flow']
    search_fields = ['referral__account__first_name', 'referral__account__username']
    list_display = ['inner_id', 'fundraiser', 'note', 'flow', 'rate', 'total', 'balance', 'created_at']
