import uuid
import random
from django.db import models, transaction
from django.utils import translation
from django.core.validators import MinValueValidator, MaxValueValidator
from django_extra_referrals.models import AbstractReceivable
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model

from django_fundraisers.fundingchema import get_funding_schema_class
from django_fundraisers.models import Fundraiser, FundraiserTransaction
from django_extra_referrals.feeschema import get_fee_schema_class
from django_extra_referrals.models import Referral, Transaction
from django_numerators.models import NumeratorMixin
from django_cashflow.models import Cash
from polymorphic.models import PolymorphicModel
from mptt.models import MPTTModel, TreeForeignKey

_ = translation.ugettext_lazy


class Agreement(MPTTModel, models.Model):
    class Meta:
        verbose_name = _("Agreement")
        verbose_name_plural = _("Agreements")

    name = models.CharField(
        max_length=80, unique=True,
        verbose_name=_('Name'))
    slug = models.SlugField(
        unique=True, max_length=80)
    parent = TreeForeignKey(
        'self', blank=True, null=True,
        related_name="children",
        on_delete=models.CASCADE)
    description = models.CharField(
        max_length=500, blank=True)

    def __str__(self):
        return self.name


class Donation(AbstractReceivable):
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Donation')
        verbose_name_plural = _('Donations')

    doc_prefix = 'DN'

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='uuid')
    fullname = models.CharField(max_length=150)
    agreement = TreeForeignKey(
        Agreement,
        null=True, blank=False,
        on_delete=models.PROTECT,
        related_name='donations',
        verbose_name=_("agreements"))
    fundraiser = models.ForeignKey(
        Fundraiser, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='donations',
        verbose_name=_("Mustahiq"),
        help_text=_('Mustahiq/Fundraiser account'))
    donation = models.DecimalField(
        default=10000,
        max_digits=15,
        decimal_places=0,
        validators=[
            MinValueValidator(10000)
        ],
        verbose_name=_("Donation"),
        help_text=_("Donation amount to be sent"))
    random = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(1000),
        ],
        verbose_name=_("Random"),
        help_text=_("Used when tracing payment"))
    payment_method = models.ForeignKey(
        Cash, null=True, blank=False,
        on_delete=models.PROTECT,
        related_name='donations',
        verbose_name=_('Payment Method'))

    def __str__(self):
        return "Donation #{}".format(self.inner_id)

    def calculate_total(self):
        self.amount = self.donation + self.random

    def confirm(self, request):
        with transaction.atomic():
            if self.referral or self.campaigner:
                fee_schema = get_fee_schema_class()
                schema = fee_schema(self)
                schema.receive_referral_balance()
            if self.fundraiser:
                funding_schema = get_funding_schema_class()
                schema = funding_schema(self)
                schema.receive_fundraiser_balance()
            self.is_paid = True
            self.is_cancelled = False
            self.save()

    def cancel(self, request):
        with transaction.atomic():
            if self.referral or self.campaigner:
                fee_schema = get_fee_schema_class()
                schema = fee_schema(self)
                schema.cancel_transaction('IN')
            if self.fundraiser:
                funding_schema = get_funding_schema_class()
                schema = funding_schema(self)
                schema.cancel_transaction('IN')
            self.is_paid = False
            self.is_cancelled = True
            self.save()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.random = random.randrange(0, 999)
        self.calculate_total()
        super().save(*args, kwargs)


class Withdraw(PolymorphicModel, NumeratorMixin):
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Withdraw')
        verbose_name_plural = _('Withdraws')

    doc_prefix = 'WD'
    parent_prefix = True
    parent_model = 'dutaziswaf_donations.Withdraw'

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='uuid')
    fullname = models.CharField(max_length=150)
    payment_method = models.ForeignKey(
        Cash, null=True, blank=False,
        on_delete=models.PROTECT,
        related_name='withdraws',
        verbose_name=_('Payment Method'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    @property
    def balance_account(self):
        return self.get_real_instance().balance_account

    def __str__(self):
        return self.fullname


class ReferralWithdraw(Withdraw):
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Referral Withdraw')
        verbose_name_plural = _('Referral Withdraws')

    referral = models.ForeignKey(
        Referral, on_delete=models.CASCADE,
        related_name='withdraws')
    transaction = GenericRelation(
        Transaction,
        related_query_name='transactions')

    def referral_schema(self):
        fee_schema = get_fee_schema_class()
        schema = fee_schema(self)
        return schema

    def confirm(self, request):
        with transaction.atomic():
            schema = self.referral_schema()
            schema.send_referral_balance()
            self.is_paid = True
            self.is_cancelled = False
            self.save()

    def cancel(self, request):
        with transaction.atomic():
            schema = self.referral_schema()
            schema.cancel_transaction('IN')
            self.is_paid = True
            self.is_cancelled = False
            self.save()


class FundraiserWithdraw(Withdraw):
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Fundraiser Withdraw')
        verbose_name_plural = _('Fundraiser Withdraws')

    fundraiser = models.ForeignKey(
        Fundraiser,
        on_delete=models.CASCADE,
        related_name='withdraws')
    transaction = GenericRelation(
        FundraiserTransaction,
        related_query_name='transactions')

    def get_fundraiser_schema(self):
        funding_schema = get_funding_schema_class()
        schema = funding_schema(self)
        return schema

    def confirm(self, request):
        with transaction.atomic():
            schema = self.get_fundraiser_schema()
            schema.send_fundraiser_balance()
            self.is_paid = True
            self.is_cancelled = False
            self.save()

    def cancel(self, request):
        with transaction.atomic():
            schema = self.get_fundraiser_schema()
            schema.cancel_transaction('IN')
            self.is_paid = True
            self.is_cancelled = False
            self.save()


class PaymentConfirmation(NumeratorMixin):
    class Meta:
        verbose_name = _("Confirmation")
        verbose_name_plural = _("Confirmations")

    doc_prefix = 'CM'

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='uuid')
    creator = models.ForeignKey(
        get_user_model(),
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='confirmations',
        verbose_name=_("Creator"))
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_('Your name.'))
    donation = models.ForeignKey(
        Donation,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Donation"))
    donation_number = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name=_("Donation Number"),
        help_text=_('Nomor transaksi donasi'))

    transfer_receipt = models.ImageField(
        verbose_name=_("Transfer receipt"))

    account_name = models.CharField(
        max_length=255,
        verbose_name=_("Account Name"),
        help_text=_('Your bank account name.'))
    account_number = models.CharField(
        max_length=255,
        verbose_name=_("Account Number"),
        help_text=_('Your bank account number.'))
    bank_name = models.CharField(
        max_length=255,
        verbose_name=_("Bank name"),
        help_text=_('Your bank account number.'))

    payment_method = models.ForeignKey(
        Cash,
        on_delete=models.PROTECT,
        related_name='confirmations',
        verbose_name=_('Payment Method'))

    amount = models.DecimalField(
        default=10000, max_digits=15, decimal_places=0,
        validators=[MinValueValidator(10000)],
        verbose_name=_("Amount"),
        help_text=_("Donation amount to be sent"))
    note = models.TextField(
        max_length=500,
        null=True, blank=True,
        verbose_name=_("Note"),
        help_text=_('Need help? please tell us.'))

    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(
        null=True, blank=True,
        editable=False,
        verbose_name=_("Verified at"))

    def __str__(self):
        return "{} / {}".format(self.inner_id, self.account_name)

    def save(self, *args, **kwargs):
        super().save(*args, kwargs)


class WithdrawRequest(NumeratorMixin):
    class Meta:
        verbose_name = _("Withdraw Request")
        verbose_name_plural = _("Withdraw Request")

    doc_prefix = 'CM'

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='uuid')
    creator = models.ForeignKey(
        get_user_model(),
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='withdraw_requests',
        verbose_name=_("Creator"))

    # TODO provide strict validation here
    fundraiser = models.ForeignKey(
        Fundraiser,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='withdraw_requests',
        verbose_name=_('Fundraiser'),
        help_text=_('Choose if you want to withdraw your fundraiser account '))

    withdraw_account_name = models.CharField(
        max_length=255,
        verbose_name=_("Account Name"),
        help_text=_('Your payment account name.'))
    withdraw_account_number = models.CharField(
        max_length=255,
        verbose_name=_("Account Number"),
        help_text=_('Your payment account number.'))
    withdraw_provider_name = models.CharField(
        max_length=255,
        verbose_name=_("Provider name"),
        help_text=_('Your payment provide name. eg. Bank Mandiri'))

    withdraw_method = models.ForeignKey(
        Cash,
        on_delete=models.PROTECT,
        limit_choices_to={'checkout': True},
        related_name='withdraw_requests',
        verbose_name=_('Payment Method'))

    amount = models.DecimalField(
        default=10000, max_digits=15, decimal_places=0,
        validators=[MinValueValidator(10000)],
        verbose_name=_("Amount"),
        help_text=_("Donation amount to be sent"))
    note = models.TextField(
        max_length=500,
        null=True, blank=True,
        verbose_name=_("Note"),
        help_text=_('Need help? please tell us.'))

    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(
        null=True, blank=True,
        editable=False,
        verbose_name=_("Verified at"))

    def __str__(self):
        return "{} / {}".format(self.inner_id, self.creator)

    def clean(self):
        # check if foundraiser is provided first
        # check foundraiser owner
        # check foundraise amount
        # check amount
        pass

    def save(self, *args, **kwargs):
        super().save(*args, kwargs)
