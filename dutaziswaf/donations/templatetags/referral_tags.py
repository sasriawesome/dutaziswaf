from django.db import models
from django.template import Library
from dutaziswaf.donations.models import Donation

register = Library()


@register.simple_tag(takes_context=True)
def referral_summary(context):
    referral = context.get('instance')

    total_donation = referral.donation_referrals.all().filter(
        is_paid=True
    ).aggregate(
        total_donation=models.Sum('amount')
    )['total_donation']

    downlines = [str(x.id) for x in referral.downlines.all()]
    downline_fundraised = Donation.objects.filter(
        referral_id__in=downlines, is_paid=True
    ).aggregate(
        sum=models.Sum('amount')
    )['sum']

    total_fundraised = downline_fundraised

    total_withdraw = referral.withdraws.all().filter(
        is_paid=True
    ).aggregate(
        total_withdraw=models.Sum('amount')
    )['total_withdraw']

    return {
        'donation_value': total_donation or 0,
        'fundraised_value': total_fundraised or 0,
        'withdraw_value': total_withdraw or 0,
        'balance_value': referral.balance or 0,
        'downlines_count': referral.downlines.count() or 0,
        'fundraisers_count': referral.account.fundraisers.count() or 0
    }


