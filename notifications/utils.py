from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from notifications.conf import settings
from notifications.compat import basestring

# Support for python2.7 and 3.4


def load_media_defaults():
    media = []
    defaults = {}
    for key, backend in settings.NOTIFICATIONS_BACKENDS.items():
        # key is a tuple (medium_id, backend_label)
        media.append(key)
        defaults[key[0]] = backend.spam_sensitivity
    return media, defaults


def notice_setting_for_user(user, notice_type, medium, scoping=None):
    """
    @@@ candidate for overriding via a hookset method so you can customize lookup at site level
    """
    kwargs = {
        "notice_type": notice_type,
        "medium": medium
    }
    if scoping:
        kwargs.update({
            "scoping_content_type": ContentType.objects.get_for_model(scoping),
            "scoping_object_id": scoping.pk
        })
    else:
        kwargs.update({
            "scoping_content_type__isnull": True,
            "scoping_object_id__isnull": True
        })
    try:
        return user.noticesetting_set.get(**kwargs)
    except ObjectDoesNotExist:
        _, NOTICE_MEDIA_DEFAULTS = load_media_defaults()
        if scoping is None:
            kwargs.pop("scoping_content_type__isnull")
            kwargs.pop("scoping_object_id__isnull")
            kwargs.update({
                "scoping_content_type": None,
                "scoping_object_id": None
            })
        default = (NOTICE_MEDIA_DEFAULTS[medium] <= notice_type.default)
        kwargs.update({"send": default})
        setting = user.noticesetting_set.create(**kwargs)
        return setting


def assemble_emails(user_list):
    email_list = []
    if isinstance(user_list, models.QuerySet):
        email_list = [row["pk"] for row in user_list.values("pk")]
    else:
        for user in user_list:
            if isinstance(user, get_user_model()):
                email_list.append(user.email)
            elif isinstance(user, basestring):
                email_list.append(user)
    return email_list


def separate_emails_and_users(value_list):
    email_list = []
    user_list = []
    for value in value_list:
        if isinstance(value, get_user_model()):
            user_list.append(value)
        elif isinstance(value, basestring):
            email_list.append(value)
    return email_list, user_list
