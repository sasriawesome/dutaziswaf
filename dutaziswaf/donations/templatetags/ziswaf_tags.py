import re
from decimal import Decimal
from django.conf import settings
from django.utils.formats import number_format
from django.template import Library

register = Library()

@register.filter('percent')
def percent(value, total):
    if total == 0:
        return 0
    return int(int(value) / int(total) * 100)


@register.filter(safe=True)
def money(value, decimal_pos=2, use_l10n=True):
    """
    Convert an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    if value is None:
        return 0
    if settings.USE_L10N and use_l10n:
        try:
            if not isinstance(value, (float, Decimal)):
                value = int(value)
        except (TypeError, ValueError):
            return money(value, False)
        else:
            return number_format(value, decimal_pos=decimal_pos, force_grouping=True)
    orig = str(value)
    new = re.sub(r"^(-?\d+)(\d{3})", r'\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return money(new, use_l10n)
