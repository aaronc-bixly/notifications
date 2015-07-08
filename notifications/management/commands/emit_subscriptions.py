import logging

from django.core.management.base import BaseCommand

from notifications.engine import send_subscriptions


class Command(BaseCommand):
    help = "Send out digests to those subscribed"

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        send_subscriptions()