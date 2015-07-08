from celery import task
from notifications.engine import send_subscriptions

@task()
def subscription_task():
    send_subscriptions()
