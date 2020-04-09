from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone, translation
from django_extra_referrals.models import Transaction as ReferralTransaction

SCHEMA_AVAILABLE = ['FLAT']
REFERRAL_SCHEMA = getattr(settings, 'REFERRAL_SCHEMA', 'FLAT')
REFERRAL_FLAT_CAMPAIGN_RATE = getattr(settings, 'REFERRAL_CAMPAIGN_RATE', 4)
REFERRAL_FLAT_UPLINES_RATE = getattr(settings, 'REFERRAL_UPLINES_RATE', [5, 2, 1])

if REFERRAL_SCHEMA not in SCHEMA_AVAILABLE:
    raise ImproperlyConfigured(
        'Please make sure REFERRAL_SCHEMA is one of {}'.format(
            ",".join(SCHEMA_AVAILABLE)
        )
    )

_ = translation.ugettext_lazy


class FeeSchema:
    referral = None
    transaction_class = ReferralTransaction

    def __init__(self, obj=None):
        if not obj.referral:
            raise ValueError('Object dont have referral')
        if not bool(obj.amount):
            raise ValueError("%s amount invalid" % obj)
        self.opts = obj._meta
        self.amount = obj.amount
        self.referral = obj.referral
        self.campaigner = obj.campaigner
        self.instance = obj

    def get_upline_rates(self):
        raise NotImplemented

    def get_campaign_rates(self):
        raise NotImplemented

    def post_referral_transaction(self, referral, rate, flow):
        transaction = ReferralTransaction(
            flow=flow,
            content_object=self.instance,
            rate=rate,
            amount=self.instance.amount,
            referral=referral,
            is_verified=True,
            verified_at=timezone.now(),
            note='%s %s' % (
                self.opts.model_name.title(),
                self.instance.inner_id
            )
        )
        transaction.save()
        referral.update_balance(transaction.balance)
        return transaction


class FlatFeeSchema(FeeSchema):
    """ Fee calculator for flat based fee"""

    CAMPAIGN_RATE = REFERRAL_FLAT_CAMPAIGN_RATE  # deprecation
    UPLINES_RATE = REFERRAL_FLAT_UPLINES_RATE  # deprecation

    def __init__(self, obj=None):
        self.rate_withdraw = 100
        self.rate_campaign = REFERRAL_FLAT_CAMPAIGN_RATE
        self.rate_uplines = REFERRAL_FLAT_UPLINES_RATE
        super().__init__(obj)

    def get_upline_rates(self):
        return self.rate_uplines

    def get_campaign_rates(self):
        return self.rate_campaign

    def receive_referral_balance(self):
        if self.referral:
            uplines = self.referral.get_uplines()
            for idx in range(uplines.count()):
                rate = self.get_upline_rates()[idx]
                upline = uplines[idx]
                self.post_referral_transaction(upline, rate, 'IN')

        if self.campaigner and not self.referral:
            rate = self.rate_campaign
            self.post_referral_transaction(self.campaigner, rate, 'IN')

    def send_referral_balance(self):
        if self.amount > self.referral.balance:
            raise ValueError("%s amount too large, %s balance is %s" % (
                self.opts.verbose_name, str(self.referral.account), self.referral.balance
            ))
        self.post_referral_transaction(self.referral, 100, 'OUT')

    def cancel_transaction(self, flow):
        reverse_flow = {'IN': 'OUT', 'OUT': 'IN'}
        if flow not in ['IN', 'OUT']:
            raise ValueError('flow must be IN or OUT')

        transactions = self.transaction_class.objects.filter(
            object_id=self.instance.id, flow=flow
        )
        for trx in transactions:
            if reverse_flow[flow] == 'OUT' and trx.total > trx.referral.balance:
                raise ValueError("%s amount too large, %s balance is %s" % (
                    self.opts.model_name, str(trx.referral.account), trx.referral.balance
                ))
            self.post_referral_transaction(trx.referral, trx.rate, reverse_flow[flow])


def get_fee_schema_class():
    schema_class = {
        'FLAT': FlatFeeSchema
    }
    return schema_class[REFERRAL_SCHEMA]
