import re
from decimal import Decimal

from django.utils.html import format_html
from django.conf import settings
from django.utils.formats import number_format


def get_money(value, use_l10n=True):
    """
    Convert an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    if settings.USE_L10N and use_l10n:
        try:
            if not isinstance(value, (float, Decimal)):
                value = int(value)
        except (TypeError, ValueError):
            return get_money(value, False)
        else:
            return number_format(value, decimal_pos=2, force_grouping=True)
    orig = str(value)
    new = re.sub(r"^(-?\d+)(\d{3})", r'\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return get_money(new, use_l10n)


def number_to_rome(number):
    """ Convert integer to rome numerals """
    numerals = {
        1: "i", 5: "v", 9: "ix", 10: "x", 40: "xl",
        50: "l", 90: "xc", 100: "c", 400: "cd", 500: "d",
        900: "cm", 1000: "m"
    }
    result = ""
    for value, numeral in sorted(numerals.items(), reverse=True):
        while number >= value:
            result += numeral
            number -= value
    return result


def format_money(number):
    text = '<div align="right">{}</div>'
    return format_html(text.format(get_money(number)))


def text_right(text):
    html_text = '<div align="right">{}</div>'
    return format_html(html_text.format(text or '-'))


def text_left(text):
    html_text = '<div align="left">{}</div>'
    return format_html(html_text.format(text or '-'))


def text_center(text):
    html_text = '<div align="center">{}</div>'
    return format_html(html_text.format(text or '-'))


def make_link(url, text):
    html_text = '<a href="{}">{}</a>'
    return format_html(html_text.format(url, text))


def number_to_text_id(nilai):
    """
    Konversi bilangan ke kalimat number_to_text_id
    :param nilai: interger
    :return: string
    """
    huruf = ["", "satu", "dua", "tiga", "empat", "lima",
             "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]
    nilai = int(nilai)
    if nilai == 0:
        return ""
    elif nilai < 12 and nilai != 0:
        return "" + huruf[nilai]
    elif nilai < 20:
        return number_to_text_id(nilai - 10) + " belas "
    elif nilai < 100:
        return number_to_text_id(nilai / 10) + " puluh " + number_to_text_id(nilai % 10)
    elif nilai < 200:
        return "seratus " + number_to_text_id(nilai - 100)
    elif nilai < 1000:
        return number_to_text_id(nilai / 100) + " ratus " + number_to_text_id(nilai % 100)
    elif nilai < 2000:
        return "seribu " + number_to_text_id(nilai - 1000)
    elif nilai < 1000000:
        return number_to_text_id(nilai / 1000) + " ribu " + number_to_text_id(nilai % 1000)
    elif nilai < 1000000000:
        return number_to_text_id(nilai / 1000000) + " juta " + number_to_text_id(nilai % 1000000)
    elif nilai < 1000000000000:
        return number_to_text_id(nilai / 1000000000) + " milyar " + number_to_text_id(nilai % 1000000000)
    elif nilai < 100000000000000:
        return number_to_text_id(nilai / 1000000000000) + " trilyun " + number_to_text_id(nilai % 1000000000000)
    elif nilai <= 100000000000000:
        return "Maaf Tidak Dapat di Proses Karena Jumlah nilai Terlalu Besar"
