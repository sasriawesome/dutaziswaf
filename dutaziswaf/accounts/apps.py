from django.apps import AppConfig as AppConfigBase


class AppConfig(AppConfigBase):
    name = 'dutaziswaf.accounts'
    label = 'dutaziswaf_accounts'
    verbose_name = 'Accounts'