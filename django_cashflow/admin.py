from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from .models import Cash, CashAccount, BankAccount, Mutation


@admin.register(CashAccount)
class CashAccountAdmin(PolymorphicChildModelAdmin):
    base_model = Cash


@admin.register(BankAccount)
class BankAccountAdmin(PolymorphicChildModelAdmin):
    base_model = Cash


@admin.register(Cash)
class PaymentAdmin(PolymorphicParentModelAdmin):
    child_models = [CashAccount, BankAccount]
    list_display = ['name', 'checkin', 'checkout', 'balance', 'modified_at']


@admin.register(Mutation)
class MutationAdmin(admin.ModelAdmin):
    list_display = [
        'inner_id',
        'cash_account',
        'created_at',
        'flow',
        'amount',
        'balance',
        'is_verified',
    ]
