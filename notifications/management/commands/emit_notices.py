import logging

from django.core.management.base import BaseCommand

from notifications.engine import send_all


class Command(BaseCommand):
    help = "Emit queued notices."

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        send_all(*args)
