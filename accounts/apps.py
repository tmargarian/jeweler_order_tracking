from django.apps import AppConfig
from allauth.account.signals import user_signed_up



class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from . import signals

        user_signed_up.connect(signals.create_user_profile)
        user_signed_up.connect(signals.create_owner)
        user_signed_up.connect(signals.create_company)
