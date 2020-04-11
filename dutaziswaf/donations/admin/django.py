from django.db import transaction
from django.contrib import admin

from django_extra_referrals.feeschema import get_fee_schema_class
from django_fundraisers.fundingchema import get_funding_schema_class

from dutaziswaf.donations.models import Donation, ReferralWithdraw, FundraiserWithdraw, Agreement


class DonationAdmin(admin.ModelAdmin):
    list_display = ['inner_id', 'fullname', 'amount', 'creator', 'referral', 'is_paid', 'is_cancelled']
    actions = ['confirm_donation', 'cancel_donation']

    def confirm_donation(self, request, queryset):
        with transaction.atomic():
            qs = queryset.filter(is_paid=False)
            for donation in qs:
                if donation.referral or donation.campaigner:
                    fee_schema = get_fee_schema_class()
                    schema = fee_schema(donation)
                    schema.receive_referral_balance()
                if donation.fundraiser:
                    funding_schema = get_funding_schema_class()
                    schema = funding_schema(donation)
                    schema.receive_fundraiser_balance()
                donation.is_paid = True
                donation.is_cancelled = False
                donation.save()

    confirm_donation.short_description = 'Confirm donations'

    def cancel_donation(self, request, queryset):
        with transaction.atomic():
            qs = queryset.filter(is_paid=True)
            for donation in qs:
                if donation.referral or donation.campaigner:
                    fee_schema = get_fee_schema_class()
                    schema = fee_schema(donation)
                    schema.cancel_transaction('IN')
                if donation.fundraiser:
                    funding_schema = get_funding_schema_class()
                    schema = funding_schema(donation)
                    schema.cancel_transaction('IN')
                donation.is_paid = False
                donation.is_cancelled = True
                donation.save()

    cancel_donation.short_description = 'Cancel donations'


class ReferralWithdrawAdmin(admin.ModelAdmin):
    referral_schema = get_fee_schema_class()
    list_display = ['inner_id', 'fullname', 'amount', 'creator', 'referral', 'is_paid', 'is_cancelled']
    actions = ['confirm_withdraw', 'cancel_withdraw']

    def confirm_withdraw(self, request, queryset):
        """ Confirm withdraw, post referral transaction """
        with transaction.atomic():
            qs = queryset.filter(is_paid=False)
            for withdraw in qs:
                schema = self.referral_schema(withdraw)
                schema.send_referral_balance()
                withdraw.is_paid = True
                withdraw.is_cancelled = False
                withdraw.save()

    def cancel_withdraw(self, request, queryset):
        """ Cancel withdraw """
        with transaction.atomic():
            qs = queryset.filter(is_paid=True)
            for withdraw in qs:
                schema = self.referral_schema(withdraw)
                schema.cancel_transaction('IN')
                withdraw.is_paid = False
                withdraw.is_cancelled = True
                withdraw.save()

    cancel_withdraw.short_description = 'Cancel withdraw'


class FundraiserWithdrawAdmin(admin.ModelAdmin):
    fundraiser_schema = get_funding_schema_class()
    list_display = ['inner_id', 'fullname', 'amount', 'creator', 'fundraiser', 'is_paid', 'is_cancelled']
    actions = ['confirm_withdraw', 'cancel_withdraw']

    def confirm_withdraw(self, request, queryset):
        """ Confirm withdraw, post referral transaction """
        with transaction.atomic():
            qs = queryset.filter(is_paid=False)
            for withdraw in qs:
                schema = self.fundraiser_schema(withdraw)
                schema.send_fundraiser_balance()
                withdraw.is_paid = True
                withdraw.is_cancelled = False
                withdraw.save()

    def cancel_withdraw(self, request, queryset):
        """ Cancel withdraw """
        with transaction.atomic():
            qs = queryset.filter(is_paid=True)
            for withdraw in qs:
                schema = self.fundraiser_schema(withdraw)
                schema.cancel_transaction('IN')
                withdraw.is_paid = False
                withdraw.is_cancelled = True
                withdraw.save()

    cancel_withdraw.short_description = 'Cancel withdraw'


admin.site.register(Donation, DonationAdmin)
admin.site.register(ReferralWithdraw, ReferralWithdrawAdmin)
admin.site.register(FundraiserWithdraw, FundraiserWithdrawAdmin)
admin.site.register(Agreement, admin.ModelAdmin)
