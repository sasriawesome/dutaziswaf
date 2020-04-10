from django.db import models
from django.template import Library
from dutaziswaf.accounts.models import get_gravatar_url

register = Library()


@register.simple_tag(takes_context=True)
def fundraiser_summary(context):
    fundraiser = context.get('instance')

    total_fundraised = fundraiser.donations.all().filter(
        is_paid=True
    ).aggregate(
        total_donation=models.Sum('amount')
    )['total_donation']

    total_withdraw = fundraiser.withdraws.all().filter(
        is_paid=True
    ).aggregate(
        total_withdraw=models.Sum('amount')
    )['total_withdraw']

    return {
        'fundraised_value': total_fundraised or 0,
        'withdraw_value': total_withdraw or 0,
        'balance_value': fundraiser.balance or 0,
        'transactions': fundraiser.transactions.all()[:10]
    }

@register.simple_tag(takes_context=True)
def fundraiser_avatar(context):
    fundraiser = context.get('instance')

    return get_gravatar_url(fundraiser.email, 144)
