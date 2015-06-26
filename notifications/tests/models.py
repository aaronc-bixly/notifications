from django.db import models

from notifications.conf import settings


class Language(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    language = models.CharField("language", max_length=10)
