import uuid
from django.db import models
from django.utils import translation, timezone
from django.core.validators import MinValueValidator
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from polymorphic.models import PolymorphicModel

from django_numerators.models import NumeratorMixin

_ = translation.ugettext_lazy


class Cash(PolymorphicModel, NumeratorMixin):
    class Meta:
        verbose_name = _("Cash")
        verbose_name_plural = _("Cashes")

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='uuid')
    name = models.CharField(
        max_length=255, verbose_name=_('Name'))
    checkin = models.BooleanField(
        default=True, verbose_name=_('Check In'))
    checkout = models.BooleanField(
        default=True, verbose_name=_('Check Out'))
    created_at = models.DateTimeField(
        default=timezone.now, editable=False)
    modified_at = models.DateTimeField(
        default=timezone.now, editable=False)
    balance = models.DecimalField(
        default=0,
        max_digits=15,
        decimal_places=2,
        editable=False,
        verbose_name=_("Balance"))

    def save_update(self):
        self.modified_at = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class CashAccount(Cash):
    class Meta:
        verbose_name = _("Cash Account")
        verbose_name_plural = _("Cash Accounts")

    doc_prefix = '1'


class BankAccount(Cash):
    class Meta:
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")

    doc_prefix = '2'
    bank_name = models.CharField(max_length=150)
    branch_office = models.CharField(null=True, blank=True, max_length=150)
    account_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=50)

    def __str__(self):
        return self.bank_name


class MutationAbstract(NumeratorMixin):
    class Meta:
        abstract = True

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='uuid')
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        blank=True, null=True,
        verbose_name=_('reference type'))
    object_id = models.CharField(
        _('reference id'),
        max_length=100,
        blank=True, null=True)
    flow = models.CharField(
        max_length=3,
        editable=False,
        choices=(('IN', 'In'), ('OUT', 'Out')),
        default='IN', verbose_name=_('Flow'))
    amount = models.DecimalField(
        default=10000, max_digits=15, decimal_places=0,
        validators=[MinValueValidator(5000)],
        verbose_name=_("Amount"),
        help_text=_("Donation amount to be sent"))
    old_balance = models.DecimalField(
        default=0,
        max_digits=15,
        decimal_places=2,
        editable=False,
        verbose_name=_("Balance"))
    balance = models.DecimalField(
        default=0,
        max_digits=15,
        decimal_places=2,
        editable=False,
        verbose_name=_("Balance"))
    note = models.TextField(
        max_length=500,
        null=True, blank=True,
        verbose_name=_("Note"),
        help_text=_('Need help? please tell us.'))
    created_at = models.DateTimeField(
        default=timezone.now, editable=False)
    is_verified = models.BooleanField(
        default=False)
    verified_at = models.DateTimeField(
        null=True, blank=True,
        editable=False,
        verbose_name=_("Verified at"))
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name='%(class)ss',
        verbose_name=_("creator"))

    def get_amount(self):
        raise NotImplementedError

    def get_cash_account(self):
        raise NotImplementedError

    def update_account_balance(self):
        raise NotImplementedError

    def increase_balance(self):
        self.balance = self.get_cash_account().balance + self.amount
        return self.balance

    def decrease_balance(self):
        self.balance = self.get_cash_account().balance - self.amount
        return self.balance

    def calculate_balance(self):
        self.old_balance = self.get_cash_account().balance
        return {'IN': self.increase_balance, 'OUT': self.decrease_balance}[self.flow]()

    def save(self, *args, **kwargs):
        self.amount = self.get_amount()
        self.calculate_balance()
        super().save(*args, **kwargs)

        # update balance
        self.update_account_balance()


class Mutation(MutationAbstract, PolymorphicModel):
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Mutation")
        verbose_name_plural = _("Mutations")

    doc_prefix = 'CS'
    parent_prefix = True
    parent_model = 'Mutation'
    cash_account = models.ForeignKey(
        Cash, on_delete=models.PROTECT,
        related_name='mutations',
        verbose_name=_('Cash Account'))
    transfer_receipt = models.ImageField(
        null=True, blank=True,
        verbose_name=_("Transfer receipt"))

    def __str__(self):
        return "{} ".format(self.inner_id)

    def get_cash_account(self):
        return self.cash_account

    def get_amount(self):
        return self.amount

    def get_reference(self):
        """Return the object represented by this mutation entry."""
        instance = self.get_real_instance()
        return instance.content_type.get_object_for_this_type(pk=instance.object_id)

    def update_account_balance(self):
        self.cash_account.balance = self.balance
        self.cash_account.save_update()


class Checkout(Mutation):
    class Meta:
        verbose_name = _("Checkout")
        verbose_name_plural = _("Checkouts")

    account_name = models.CharField(
        max_length=255,
        verbose_name=_("Account Name"),
        help_text=_('Destination account/holder name.'))
    account_number = models.CharField(
        max_length=255,
        verbose_name=_("Account Number"),
        help_text=_('Destination account number.'))
    provider_name = models.CharField(
        max_length=255,
        verbose_name=_("Provider name"),
        help_text=_('Destination provider. (Bank Mandiri or Gopay)'))

    def save(self, *args, **kwargs):
        self.flow = 'OUT'
        super().save(*args, kwargs)


class Checkin(Mutation):
    class Meta:
        verbose_name = _("Checkin")
        verbose_name_plural = _("Checkins")

    account_name = models.CharField(
        max_length=255,
        verbose_name=_("Account Name"),
        help_text=_('Origin account/holder name.'))
    account_number = models.CharField(
        max_length=255,
        verbose_name=_("Account Number"),
        help_text=_('Origin account number.'))
    provider_name = models.CharField(
        max_length=255,
        verbose_name=_("Provider name"),
        help_text=_('Origin provider. (Bank Mandiri or Gopay)'))

    def save(self, *args, **kwargs):
        self.flow = 'IN'
        super().save(*args, kwargs)


class PayableMixin(models.Model):
    class Meta:
        abstract = True

    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Paid at"))
    is_paid = models.BooleanField(default=False, verbose_name=_("Paid at"))

    def make_paid(self):
        self.paid_at = timezone.now()
        self.is_paid = True
        self.save()
