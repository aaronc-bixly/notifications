from __future__ import unicode_literals
from __future__ import print_function

import base64
import json

from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language, activate
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from six.moves import cPickle
from notifications.utils import load_media_defaults, assemble_emails, separate_emails_and_users
from notifications.conf import settings

NOTICE_MEDIA, NOTICE_MEDIA_DEFAULTS = load_media_defaults()


class LanguageStoreNotAvailable(Exception):
    pass


@python_2_unicode_compatible
class NoticeType(models.Model):
    label = models.CharField(_("label"), max_length=40)
    display = models.CharField(_("display"), max_length=50)
    description = models.CharField(_("description"), max_length=100)
    assets = models.TextField(_("assets"), null=True, blank=True)

    objects = models.Manager()
    # by default only on for media with sensitivity less than or equal to this number
    default = models.IntegerField(_("default"))

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _("Notice Type")
        verbose_name_plural = _("Notice Types")

    def set_assets(self, asset_list):
        self.extra_context = json.dumps(asset_list)

    def get_assets(self):
        if self.assets is not None:
            return json.loads(self.assets)
        else:
            return []

    @classmethod
    def create(cls, label, display, description, assets=None, default=2, verbosity=0):
        """
        Creates a new NoticeType.
        This is intended to be used by other apps as a post_migrate manangement step.
        """
        if assets:
            assets = json.dumps(assets)
        try:
            notice_type = cls.objects.get(label=label)
            updated = False
            if display != notice_type.display:
                notice_type.display = display
                updated = True
            if description != notice_type.description:
                notice_type.description = description
                updated = True
            if default != notice_type.default:
                notice_type.default = default
                updated = True
            if assets != notice_type.assets:
                notice_type.assets = assets
                updated = True
            if updated:
                notice_type.save()
                if verbosity > 1:
                    print("Updated %s NoticeType" % label)
        except cls.DoesNotExist:
            cls(label=label, display=display, description=description, assets=assets, default=default).save()
            if verbosity > 1:
                print("Created %s NoticeType" % label)


class NoticeSetting(models.Model):
    """
    Indicates, for a given user, whether to send notifications
    of a given type to a given medium.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_("notice type"))
    medium = models.CharField(_("medium"), max_length=1, choices=NOTICE_MEDIA)
    send = models.BooleanField(_("send"), default=False)
    scoping_content_type = models.ForeignKey(ContentType, null=True, blank=True)
    scoping_object_id = models.PositiveIntegerField(null=True, blank=True)
    scoping = GenericForeignKey("scoping_content_type", "scoping_object_id")

    class Meta:
        verbose_name = _("Notice Setting")
        verbose_name_plural = _("Notice Settings")
        unique_together = ("user", "notice_type", "medium", "scoping_content_type", "scoping_object_id")


class NoticeQueueBatch(models.Model):
    """
    A queued notice.
    Denormalized data for a notice.
    """
    pickled_data = models.TextField()
    send_at = models.DateTimeField(null=True, blank=True)


class NoticeHistory(models.Model):
    """
    Stores information of previously sent notifications.
    """
    notice_type = models.ForeignKey(NoticeType)
    recipient = models.ManyToManyField(settings.AUTH_USER_MODEL, through='NoticeThrough')
    sender = models.TextField()
    extra_context = models.TextField(null=True, blank=True)
    attachments = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(editable=False)

    class Meta:
        verbose_name = _("Notice History")
        verbose_name_plural = _("Notice History")

    def save(self, *args, **kwargs):
        if not self.id:
            self.sent_at = timezone.now()
        return super(NoticeHistory, self).save(*args, **kwargs)

    def set_extra_context(self, context_dict):
        value = json.dumps(context_dict)
        self.extra_context = value

    def get_extra_context(self):
        if self.extra_context is not None:
            return json.loads(self.extra_context)
        else:
            return {}

    def set_attachments(self, attach_list):
        value = json.dumps(attach_list)
        self.attachments = value

    def get_attachments(self):
        if self.attachments is not None:
            return json.loads(self.attachments)
        else:
            return []


class NoticeThrough(models.Model):
    """
    Through model for history and users, please ignore.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    history = models.ForeignKey(NoticeHistory)


def get_notification_language(user):
    """
    Returns site-specific notification language for this user. Raises
    LanguageStoreNotAvailable if this site does not use translated
    notifications.
    """
    if settings.NOTIFICATIONS_LANGUAGE_MODEL:
        model = settings.NOTIFICATIONS_GET_LANGUAGE_MODEL()
        try:
            language = model._default_manager.get(user__id__exact=user.id)
            if hasattr(language, "language"):
                return language.language
        except (ImportError, ImproperlyConfigured, model.DoesNotExist):
            raise LanguageStoreNotAvailable
    raise LanguageStoreNotAvailable


def send_now(users, label, extra_context=None, sender=None, scoping=None, attachments=None, **kwargs):
    """
    Creates a new notice.
    This is intended to be how other apps create new notices.
    """
    sent = False
    if sender is None:
        sender = settings.DEFAULT_FROM_EMAIL
    if extra_context is None:
        extra_context = {}
    if attachments is None:
        attachments = []

    email_list, user_list = separate_emails_and_users(users)
    UserModel = get_user_model()
    for email in email_list:
        try:
            user = UserModel.objects.get(email=email)
            user_list.append(user)
            email_list.remove(email)
        except UserModel.DoesNotExist:
            pass

    notice_type = NoticeType.objects.get(label=label)
    current_language = get_language()

    sent_users = []
    for user in user_list:
        # get user language for user from language store defined in
        # NOTIFICATION_LANGUAGE_MODULE setting
        try:
            language = get_notification_language(user)
            activate(language)
        except LanguageStoreNotAvailable:
            pass

        for backend in settings.NOTIFICATIONS_BACKENDS.values():
            if backend.can_send(user, notice_type, scoping=scoping):
                backend.deliver(notice_type, extra_context, attachments, user.email, sender)
                sent = True
                sent_users.append(user)

        # reset environment to original language
        activate(current_language)

    for email in email_list:
        backend = settings.NOTIFICATIONS_DEFAULT_BACKEND
        backend.deliver(notice_type, extra_context, attachments, email, sender)

    history = NoticeHistory(notice_type=notice_type, sender=sender, extra_context=json.dumps(extra_context),
                            attachments=json.dumps(attachments))
    history.save()
    throughlist = []
    for user_email in sent_users:
        throughlist.append(NoticeThrough(user=user_email, history=history))
    NoticeThrough.objects.bulk_create(throughlist)

    return sent


def send(*args, **kwargs):
    """
    A basic interface around both queue and send_now. This honors a global
    flag NOTIFICATION_QUEUE_ALL that helps determine whether all calls should
    be queued or not. A per call ``queue`` or ``now`` keyword argument can be
    used to always override the default global behavior.
    """
    queue_flag = kwargs.pop("queue", False)
    now_flag = kwargs.pop("now", False)
    assert not (queue_flag and now_flag), "'queue' and 'now' cannot both be True."
    if queue_flag:
        return queue(*args, **kwargs)
    elif now_flag:
        return send_now(*args, **kwargs)
    else:
        if settings.NOTIFICATIONS_QUEUE_ALL:
            return queue(*args, **kwargs)
        else:
            return send_now(*args, **kwargs)


def queue(users, label, extra_context=None, sender=None, send_at=None, attachments=None):
    """
    Queue the notification in NoticeQueueBatch. This allows for large amounts
    of user notifications to be deferred to a seperate process running outside
    the webserver.
    """
    if extra_context is None:
        extra_context = {}
    if attachments is None:
        attachments = {}
    user_list = assemble_emails(users)
    notices = []
    for user in user_list:
        notices.append((user, label, extra_context, sender, attachments))
    NoticeQueueBatch(pickled_data=base64.b64encode(cPickle.dumps(notices)), send_at=send_at).save()
