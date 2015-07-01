import base64

from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from six.moves import cPickle
from notifications.models import NoticeType, NoticeQueueBatch, NoticeSetting, NoticeHistory
from notifications.models import LanguageStoreNotAvailable
from notifications.models import get_notification_language, send_now, send, queue
from notifications.conf import settings
from . import get_backend_id


class BaseTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("test_user", "test@user.com", "123456")
        self.user2 = get_user_model().objects.create_user("test_user2", "test2@user.com", "123456")
        NoticeType.create("label", "display", "description")
        self.notice_type = NoticeType.objects.get(label="label")

    def tearDown(self):
        self.user.delete()
        self.user2.delete()
        self.notice_type.delete()


class TestNoticeType(TestCase):

    def test_create(self):
        label = "friends_invite"
        NoticeType.create(label, "Invitation Received", "you received an invitation", default=2,
                          verbosity=2)
        n = NoticeType.objects.get(label=label)
        self.assertEqual(str(n), label)
        # update
        NoticeType.create(label, "Invitation for you", "you got an invitation", default=1,
                          verbosity=2)
        n = NoticeType.objects.get(pk=n.pk)
        self.assertEqual(n.display, "Invitation for you")
        self.assertEqual(n.description, "you got an invitation")
        self.assertEqual(n.default, 1)


class TestProcedures(BaseTest):
    def setUp(self):
        super(TestProcedures, self).setUp()
        mail.outbox = []

    def tearDown(self):
        super(TestProcedures, self).tearDown()
        NoticeQueueBatch.objects.all().delete()

    @override_settings(SITE_ID=1)
    def test_send_now(self):
        Site.objects.create(domain="localhost", name="localhost")
        users = [self.user, self.user2]
        send_now(users, "label")
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn(self.user2.email, mail.outbox[1].to)
        self.assertEqual(len(NoticeHistory.objects.all()), 1)
        not_his = NoticeHistory.objects.get(pk=1)
        self.assertEqual(len(not_his.recipient.all()), 2)

    @override_settings(SITE_ID=1)
    def test_send(self):
        self.assertRaises(AssertionError, send, queue=True, now=True)

        users = [self.user, self.user2]
        send(users, "label", now=True)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn(self.user2.email, mail.outbox[1].to)

        send(users, "label", queue=True)
        self.assertEqual(NoticeQueueBatch.objects.count(), 1)
        batch = NoticeQueueBatch.objects.all()[0]
        notices = cPickle.loads(base64.b64decode(batch.pickled_data))
        self.assertEqual(len(notices), 2)

    @override_settings(SITE_ID=1)
    def test_send_default(self):
        # default behaviour, send_now
        users = [self.user, self.user2]
        send(users, "label")
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(NoticeQueueBatch.objects.count(), 0)

    @override_settings(SITE_ID=1)
    def test_queue_queryset(self):
        users = get_user_model().objects.all()
        queue(users, "label")
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(NoticeQueueBatch.objects.count(), 1)

    @override_settings(SITE_ID=1)
    def test_non_user_send(self):
        emails = ["one@test.com", "two@test.com"]
        send(emails, "label")
        self.assertEqual(len(mail.outbox), 2)

    @override_settings(SITE_ID=1)
    def test_mixed_user_send(self):
        emails = [self.user, "one@test.com"]
        send(emails, "label")
        self.assertEqual(len(mail.outbox), 2)

        emails.append(self.user2)
        send(emails, "label")
        self.assertEqual(len(mail.outbox), 5)

        emails.append("two@test.com")
        emails.append("three@test.com")
        send(emails, "label")
        self.assertEqual(len(mail.outbox), 10)
        self.assertEqual(len(NoticeHistory.objects.all()), 3)
