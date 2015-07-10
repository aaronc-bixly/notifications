from django.apps import AppConfig as BaseAppConfig
from django.db.models.signals import post_migrate

from djcelery.models import PeriodicTask, CrontabSchedule


def create_periodic_task(sender, **kwargs):
    crontab, created = CrontabSchedule.objects.get_or_create(minute='*', hour='8', day_of_week='*', day_of_month='*', month_of_year='*')
    PeriodicTask.objects.get_or_create(name="Notification: Emit Subscriptions", task="notifications.tasks.subscription_task", crontab=crontab, interval=None)


class AppConfig(BaseAppConfig):

    name = "notifications"
    verbose_name = "Notifications"

    def ready(self):
        post_migrate.connect(create_periodic_task, sender=self)
