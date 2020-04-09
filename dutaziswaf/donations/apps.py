from django.apps import AppConfig as AppConfigBase


class AppConfig(AppConfigBase):
    name = 'dutaziswaf.donations'
    label = 'dutaziswaf_donations'
    verbose_name = 'Donations'
