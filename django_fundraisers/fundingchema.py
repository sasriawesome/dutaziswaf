from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone, translation

from .models import FundraiserTransaction

FUNDRAISER_SCHEMA = getattr(settings, 'FUNDRAISER_SCHEMA', 'FLAT')
FUNDRAISER_FLAT_RATE = getattr(settings, 'FUNDRAISER_FLAT_RATE', 70)
FUNDRAISING_SCHEMAS = ['FLAT']

_ = translation.ugettext_lazy

if FUNDRAISER_SCHEMA not in FUNDRAISING_SCHEMAS:
    raise ImproperlyConfigured(
        'Please make sure FUNDRAISER_SCHEMA is one of {}'.format(
            ",".join(FUNDRAISING_SCHEMAS)
        )
    )


class FundingSchema:
    referral = None
    transaction_class = FundraiserTransaction

    def __init__(self, obj=None):
        if not obj.fundraiser:
            raise ValueError('Object dont have fundraiser')
        if not bool(obj.amount):
            raise ValueError("%s amount invalid" % obj)
        self.opts = obj._meta
        self.amount = obj.amount
        self.fundraiser = obj.fundraiser
        self.share_rate = FUNDRAISER_FLAT_RATE
        self.instance = obj

    def get_donation_share_rates(self):
        raise NotImplementedError

    def post_fundraiser_transaction(self, rate, flow):
        transaction = FundraiserTransaction(
            flow=flow,
            content_object=self.instance,
            rate=rate,
            amount=self.instance.amount,
            fundraiser=self.fundraiser,
            is_verified=True,
            verified_at=timezone.now(),
            note='%s %s' % (
                self.opts.model_name.title(),
                self.instance.inner_id
            )
        )
        transaction.save()
        self.fundraiser.update_balance(transaction.balance)
        return transaction


class FlatFundingSchema(FundingSchema):
    """ Fee calculator for flat based fee"""

    def __init__(self, obj=None):
        self.share_rate = FUNDRAISER_FLAT_RATE
        self.withdraw_rate = 100
        super().__init__(obj)

    def get_donation_share_rates(self):
        return self.share_rate

    def receive_fundraiser_balance(self):
        if not bool(self.instance.amount):
            raise ValueError("%s amount invalid" % self.opts.model_name.title())
        self.post_fundraiser_transaction(self.share_rate, 'IN')

    def send_fundraiser_balance(self):
        if self.amount > self.fundraiser.balance:
            raise ValueError("%s amount too large, %s balance is %s" % (
                self.opts.model_name, self.fundraiser.name, self.fundraiser.balance
            ))
        self.post_fundraiser_transaction(self.withdraw_rate, 'OUT')

    def cancel_transaction(self, flow):
        reverse_flow = {'IN': 'OUT', 'OUT': 'IN'}
        if flow not in ['IN', 'OUT']:
            raise ValueError('flow must be IN or OUT')

        transactions = self.transaction_class.objects.filter(
            object_id=self.instance.id, flow=flow
        )
        for trx in transactions:
            if reverse_flow[flow] == 'OUT' and trx.total > trx.fundraiser.balance:
                raise ValueError("%s amount too large, %s balance is %s" % (
                    self.opts.model_name, str(trx.fundraiser.account), trx.fundraiser.balance
                ))
            self.post_fundraiser_transaction(trx.rate, reverse_flow[flow])


def get_funding_schema_class():
    schema_class = {
        'FLAT': FlatFundingSchema
    }
    return schema_class[FUNDRAISER_SCHEMA]
