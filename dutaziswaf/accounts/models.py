import enum
import hashlib
from urllib import parse
from django.db import models
from django.db.utils import cached_property
from django.utils import translation
from django.contrib.auth.models import AbstractUser

_ = translation.ugettext_lazy


def get_gravatar_url(email, size=50):
    default = "mm"
    size = int(size) * 2  # requested at retina size by default and scaled down at point of use with css
    gravatar_provider_url = '//www.gravatar.com/avatar'

    if (not email) or (gravatar_provider_url is None):
        return None

    gravatar_url = "{gravatar_provider_url}/{hash}?{params}".format(
        gravatar_provider_url=gravatar_provider_url.rstrip('/'),
        hash=hashlib.md5(email.lower().encode('utf-8')).hexdigest(),
        params=parse.urlencode({'s': size, 'd': default})
    )

    return gravatar_url


class User(AbstractUser):
    avatar_size = 144
    avatar_default = 'mp'  # "https://www.example.com/default.jpg"
    is_mustahiq = models.BooleanField(default=False)
    is_muzakki = models.BooleanField(default=True)

    def __str__(self):
        return self.get_full_name()

    @property
    def avatar(self):
        return get_gravatar_url(self.email, self.avatar_size)
