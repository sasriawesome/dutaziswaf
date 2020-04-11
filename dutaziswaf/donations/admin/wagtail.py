from django.utils import translation
from django.conf.urls import url
from django.shortcuts import HttpResponse
from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, ObjectList

from django_extra_referrals.models import Referral, Transaction
from django_fundraisers.models import Fundraiser, FundraiserTransaction
from django_cashflow.models import CashAccount, BankAccount

from dutaziswaf.donations.models import (
    Donation, Agreement, PaymentConfirmation, FundraiserWithdraw, ReferralWithdraw)

from .helpers import (
    ReadOnlyPermissionHelper,
    DonationPermissionHelper,
    WithdrawPermissionHelper,
    ConfirmCancelButtonHelper,
    ConfirmCancelURLHelper,
)
from .views import (
    ConfirmView, CancelView
)

_ = translation.ugettext_lazy


class AgreementModelAdmin(ModelAdmin):
    menu_icon = 'fa-handshake-o',
    menu_label = _('Agreements')
    model = Agreement


class BankAccountModelAdmin(ModelAdmin):
    model = BankAccount
    menu_icon = 'fa-institution',
    menu_label = _('Bank Accounts')
    list_display = ['name', 'bank_name', 'branch_office', 'account_name', 'account_number', 'checkin', 'checkout']

    edit_handler = ObjectList([
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('bank_name'),
            FieldPanel('branch_office'),
            FieldPanel('account_name'),
            FieldPanel('account_number'),
            FieldPanel('checkin'),
            FieldPanel('checkout'),
        ])
    ])


class CashAccountModelAdmin(ModelAdmin):
    model = CashAccount
    menu_icon = 'fa-dollar',
    menu_label = _('Cash Accounts')
    list_display = ['name', 'checkin', 'checkout']

    edit_handler = ObjectList([
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('checkin'),
            FieldPanel('checkout'),
        ])
    ])


class FundraiserModelAdmin(ModelAdmin):
    model = Fundraiser
    inspect_view_enabled = True
    menu_icon = 'fa-user-circle-o',
    menu_label = _('Fundraisers')
    list_display = ['inner_id', 'name', 'founder', 'balance']

    edit_handler = ObjectList([
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('founder'),
            FieldPanel('year_founded'),
            FieldPanel('mission'),
            FieldPanel('is_organization'),
            FieldPanel('is_verified'),
            FieldPanel('is_active'),
        ], heading=_('Basic informations')),
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('phone1'),
            FieldPanel('whatsapp'),
            FieldPanel('website'),
        ], heading=_('Contact')),
        MultiFieldPanel([
            FieldPanel('street'),
            FieldPanel('city'),
            FieldPanel('province'),
            FieldPanel('country'),
            FieldPanel('zipcode'),
        ], heading=_('Address')),
    ])


class FundraiserTransactionModelAdmin(ModelAdmin):
    model = FundraiserTransaction
    permission_helper_class = ReadOnlyPermissionHelper
    inspect_view_enabled = True
    menu_icon = 'fa-list-ul',
    menu_label = _('Transactions')
    list_filter = ['created_at', 'flow']
    list_select_related = ['fundraiser']
    search_fields = ['fundraiser__name']
    list_display = ['fundraiser', 'note', 'flow', 'total', 'created_at']


class ReferralModelAdmin(ModelAdmin):
    model = Referral
    inspect_view_enabled = True
    menu_icon = 'fa-user-circle-o',
    menu_label = _('Referrals')
    list_select_related = ['account', 'parent']
    search_fields = ['account__first_name', 'account__last_name']
    list_display = ['inner_id', 'account', 'parent', 'decendants', 'downlines', 'level', 'created_at', 'balance']

    def decendants(self, obj):
        return obj.get_descendant_count()

    def downlines(self, obj):
        return obj.downlines.count()

    def get_queryset(self, request):
        return super().get_queryset(request).only('inner_id', 'account', 'parent')

    edit_handler = ObjectList([
        MultiFieldPanel([
            FieldPanel('parent'),
            FieldPanel('account'),
        ])
    ])


class ReferralTransactionModelAdmin(ModelAdmin):
    model = Transaction
    permission_helper_class = ReadOnlyPermissionHelper
    inspect_view_enabled = True
    menu_icon = 'fa-list-ul',
    menu_label = _('Transactions')
    list_filter = ['created_at', 'flow']
    list_select_related = ['referral']
    search_fields = ['referral__account__first_name', 'referral__account__username']
    list_display = ['referral', 'note', 'flow', 'total', 'created_at']


class ConfirmCancelAdminMixin(ModelAdmin):
    button_helper_class = ConfirmCancelButtonHelper
    url_helper_class = ConfirmCancelURLHelper
    confirm_view_class = ConfirmView
    cancel_view_class = CancelView

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        urls += (
            url(self.url_helper.get_action_url_pattern('confirm'),
                self.confirm_view,
                name=self.url_helper.get_action_url_name('confirm')),
            url(self.url_helper.get_action_url_pattern('cancel'),
                self.cancel_view,
                name=self.url_helper.get_action_url_name('cancel')),
        )
        return urls

    def confirm_view(self, request, instance_pk):
        kwargs = {'model_admin': self, 'instance_pk': instance_pk}
        view_class = self.confirm_view_class
        return view_class.as_view(**kwargs)(request)

    def cancel_view(self, request, instance_pk):
        kwargs = {'model_admin': self, 'instance_pk': instance_pk}
        view_class = self.cancel_view_class
        return view_class.as_view(**kwargs)(request)


class DonationModelAdmin(ConfirmCancelAdminMixin, ModelAdmin):
    model = Donation
    inspect_view_enabled = True
    permission_helper_class = DonationPermissionHelper
    menu_icon = 'fa-list-ul',
    menu_label = _('Donations')
    list_select_related = ['creator', 'referral', 'campaigner', 'fundraiser']
    search_fields = ['fullname', 'creator__first_name', 'creator__last_name', 'creator__user_name']
    list_display = ['inner_id', 'fullname', 'amount', 'fundraiser', 'referral', 'campaigner', 'is_paid', 'is_cancelled']

    edit_handler = ObjectList([
        MultiFieldPanel([
            FieldPanel('fullname'),
            FieldPanel('agreement'),
            FieldPanel('referral'),
            FieldPanel('fundraiser'),
            # FieldPanel('campaigner'),
            FieldPanel('payment_method'),
            FieldPanel('donation'),
        ])
    ])


class ReferralWithdrawModelAdmin(ConfirmCancelAdminMixin, ModelAdmin):
    model = ReferralWithdraw
    inspect_view_enabled = True
    permission_helper_class = WithdrawPermissionHelper
    menu_icon = 'fa-list-ul',
    menu_label = _('Withdraw')
    list_display = ['inner_id', 'referral', 'amount', 'creator', 'is_paid', 'is_cancelled']

    edit_handler = ObjectList([
        MultiFieldPanel([
            FieldPanel('fullname'),
            FieldPanel('referral'),
            FieldPanel('payment_method'),
            FieldPanel('amount'),
            FieldPanel('creator'),
        ])
    ])


class FundraiserWithdrawModelAdmin(ConfirmCancelAdminMixin, ModelAdmin):
    model = FundraiserWithdraw
    inspect_view_enabled = True
    permission_helper_class = WithdrawPermissionHelper
    menu_icon = 'fa-list-ul',
    menu_label = _('Withdraw')
    list_display = ['inner_id', 'fundraiser', 'amount', 'creator', 'is_paid', 'is_cancelled']

    edit_handler = ObjectList([
        MultiFieldPanel([
            FieldPanel('fullname'),
            FieldPanel('fundraiser'),
            FieldPanel('payment_method'),
            FieldPanel('amount'),
            FieldPanel('creator'),
        ])
    ])


class PaymentConfirmationModelAdmin(ModelAdmin):
    model = PaymentConfirmation
    menu_icon = 'fa-comments-o',
    menu_label = _('Confirmations')
    list_filter = ['created_at', 'is_verified', 'verified_at', ]
    list_display = [
        'created_at',
        'creator',
        'donation_number',
        'account_name',
        'account_number',
        'bank_name',
        'payment_method',
        'amount',
        'note',
    ]

    edit_handler = ObjectList([
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('donation_number'),
            FieldPanel('amount'),
            FieldPanel('note'),
        ], heading=_("Informasi")),
        MultiFieldPanel([
            FieldPanel('transfer_receipt'),
            FieldPanel('account_name'),
            FieldPanel('account_number'),
            FieldPanel('bank_name'),
            FieldPanel('payment_method'),
        ], heading=_("Informasi Pengiriman"))
    ])


class ReferralModelAdminGroup(ModelAdminGroup):
    menu_icon = 'fa-user-circle-o',
    menu_label = _('Referrals')
    items = [
        ReferralModelAdmin,
        ReferralTransactionModelAdmin,
        ReferralWithdrawModelAdmin
    ]


class FundraiserModelAdminGroup(ModelAdminGroup):
    menu_icon = 'fa-user-circle-o',
    menu_label = _('Fundraisers')
    items = [
        FundraiserModelAdmin,
        FundraiserTransactionModelAdmin,
        FundraiserWithdrawModelAdmin
    ]


class DonationModelAdminGroup(ModelAdminGroup):
    menu_icon = 'fa-heart',
    menu_label = _('Fundraising')
    items = [
        AgreementModelAdmin,
        DonationModelAdmin,
        PaymentConfirmationModelAdmin
    ]


class PaymentModelAdminGroup(ModelAdminGroup):
    menu_icon = 'fa-dollar',
    menu_label = _('Payments')
    items = [
        CashAccountModelAdmin,
        BankAccountModelAdmin
    ]


modeladmin_register(DonationModelAdminGroup)
modeladmin_register(ReferralModelAdminGroup)
modeladmin_register(FundraiserModelAdminGroup)
modeladmin_register(PaymentModelAdminGroup)

# from .admin_django import *
