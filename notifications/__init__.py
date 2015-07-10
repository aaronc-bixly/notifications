from notifications.models import send, queue, send_now
from notifications.engine import send_digest, send_all, send_subscriptions

__version__ = "1.0.0"

default_app_config = "notifications.apps.AppConfig"
