import sys
import time
import logging
import traceback
import base64

from django.utils import timezone
from django.core.mail import mail_admins
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from six.moves import cPickle as pickle
from notifications.models import NoticeQueueBatch, send_now, NoticeHistory
from notifications.signals import emitted_notices
from notifications.conf import settings


def send_all(*args):
    batches, sent, sent_actual = 0, 0, 0
    start_time = time.time()

    try:
        for queued_batch in NoticeQueueBatch.objects.all():
            if queued_batch.send_at is None or queued_batch.send_at < timezone.now():
                notices = pickle.loads(base64.b64decode(queued_batch.pickled_data))
                for user, label, extra_context, sender, attachments in notices:
                    try:
                        user = get_user_model().objects.get(pk=user)
                        logging.info("emitting notice {0} to {1}".format(label, user))
                        # call this once per user to be atomic and allow for logging to
                        # accurately show how long each takes.
                        if send_now(users=[user], label=label, extra_context=extra_context, sender=sender, attachments=attachments):
                            sent_actual += 1
                    except get_user_model().DoesNotExist:
                        # Ignore deleted users, just warn about them
                        logging.warning(
                            "not emitting notice {0} to user {1} since it does not exist".format(
                                label,
                                user)
                        )
                    sent += 1
                queued_batch.delete()
                batches += 1
        emitted_notices.send(
            sender=NoticeQueueBatch,
            batches=batches,
            sent=sent,
            sent_actual=sent_actual,
            run_time="%.2f seconds" % (time.time() - start_time)
        )
    except Exception:
        # get the exception
        _, e, _ = sys.exc_info()
        # email people
        current_site = Site.objects.get_current()
        subject = "[{0} emit_notices] {1}".format(current_site.name, e)
        message = "\n".join(
            traceback.format_exception(*sys.exc_info())
        )
        mail_admins(subject, message, fail_silently=True)
        # log it as critical
        logging.critical("an exception occurred: {0}".format(e))

    logging.info("")
    logging.info("{0} batches, {1} sent".format(batches, sent,))
    logging.info("done in {0:.2f} seconds".format(time.time() - start_time))


def send_digest(users, notice_types, **kwargs):
    notice_history = collect_notifications(notice_types, **kwargs)
    for backend in settings.NOTIFICATIONS_BACKENDS.values():
        backend.deliver_digest(users, notice_history)


def collect_notifications(notice_types='__all__', days=1, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    time_depth = timezone.now() - timezone.timedelta(days=days, seconds=seconds, microseconds=microseconds,
                                                     milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)
    if notice_types == '__all__':
        return NoticeHistory.objects.filter(sent_at__gte=time_depth)
    elif hasattr(notice_types, '__iter__'):
        return NoticeHistory.objects.filter(sent_at__gte=time_depth, notice_type__label__in=notice_types)
    else:
        return None