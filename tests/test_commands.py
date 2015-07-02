from django.utils import timezone
from django.core import management, mail
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model

from notifications.models import NoticeType, queue, NoticeQueueBatch, send_now, NoticeHistory
from notifications.engine import send_digest


class TestManagementCmd(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("test_user", "test@user.com", "123456")
        self.user2 = get_user_model().objects.create_user("test_user2", "test2@user.com", "123456")
        NoticeType.create("label", "display", "description")
        NoticeType.create("label2", "display2", "description2")
        NoticeType.create("different", "display Different", "description3")

    @override_settings(SITE_ID=1)
    def test_emit_notices(self):
        users = [self.user, self.user2]
        queue(users, "label")
        queue(users, "label", send_at=timezone.now())
        queue(users, "label", send_at=(timezone.now() + timezone.timedelta(minutes=10)))
        management.call_command("emit_notices")
        self.assertEqual(len(mail.outbox), 4)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn(self.user2.email, mail.outbox[1].to)
        self.assertEqual(len(NoticeQueueBatch.objects.all()), 1)

    @override_settings(SITE_ID=1)
    def test_history_collection(self):
        send_now([self.user], "label")
        send_now([self.user], "label")
        send_now([self.user], "label2")
        send_now([self.user], "different")
        query = NoticeHistory.objects.filter(notice_type__label__in=["label"])
        self.assertEqual(len(query), 2)
        query = NoticeHistory.objects.filter(notice_type__label__in=["label2"])
        self.assertEqual(len(query), 1)
        query = NoticeHistory.objects.filter(notice_type__label__in=["different"])
        self.assertEqual(len(query), 1)
        query = NoticeHistory.objects.filter(notice_type__label__in=["label", "label2", "different"])
        self.assertEqual(len(query), 4)
        query = NoticeHistory.objects.filter(sent_at__gte=(timezone.now() - timezone.timedelta(days=1)),  notice_type__label__in=["label", "label2", "different"])
        self.assertEqual(len(query), 4)
        query = NoticeHistory.objects.filter(sent_at__gte=timezone.now(),  notice_type__label__in=["label", "label2", "different"])
        self.assertEqual(len(query), 0)

    @override_settings(SITE_ID=1)
    def test_digest_creator(self):
        send_now([self.user], "label")
        send_now([self.user], "label")
        send_now([self.user], "label2")
        send_digest([self.user2], ["label"])
        self.assertEqual(len(mail.outbox), 4)
        send_digest([self.user2], ["label", "label2"])
        self.assertEqual(len(mail.outbox), 5)
