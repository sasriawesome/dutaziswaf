from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from .models import Cash, CashAccount, BankAccount, Mutation, Checkout, Checkin


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
class MutationAdmin(PolymorphicParentModelAdmin):
    child_models = [Checkout, Checkin]
    list_display = [
        'inner_id',
        'cash_account',
        'created_at',
        'flow',
        'amount',
        'balance',
        'is_verified',
    ]


@admin.register(Checkin)
class CheckinAdmin(PolymorphicChildModelAdmin):
    base_model = Mutation
    fields = [
        'content_type',
        'object_id',
        'account_name',
        'account_number',
        'provider_name',
        'amount',
        'cash_account',
        'transfer_receipt',
        'note',
        'is_verified',
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Checkout)
class CheckoutAdmin(PolymorphicChildModelAdmin):
    base_model = Mutation
    fields = [
        'content_type',
        'object_id',
        'account_name',
        'account_number',
        'provider_name',
        'amount',
        'cash_account',
        'transfer_receipt',
        'note',
        'is_verified',
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
