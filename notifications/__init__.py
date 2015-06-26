import pkg_resources


__version__ = pkg_resources.get_distribution("notifications").version

default_app_config = "notifications.apps.AppConfig"
