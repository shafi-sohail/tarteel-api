from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ProfilesConfig(AppConfig):
    name = 'profiles'
    verbose_name = _('profiles')

    def ready(self):
        from profiles import signals
