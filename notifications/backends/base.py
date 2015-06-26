from django.template import Context
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from ..conf import settings
from notifications.utils import notice_setting_for_user


class BaseBackend(object):
    """
    The base backend.
    """
    def __init__(self, medium_id, spam_sensitivity=None):
        self.medium_id = medium_id
        if spam_sensitivity is not None:
            self.spam_sensitivity = spam_sensitivity

    def can_send(self, user, notice_type, scoping):
        """
        Determines whether this backend is allowed to send a notification to
        the given user and notice_type.
        """
        return notice_setting_for_user(user, notice_type, self.medium_id, scoping).send

    def deliver(self, recipient, sender, notice_type, extra_context):
        """
        Deliver a notification to the given recipient.
        """
        raise NotImplementedError()

    def get_formatted_message(self, format, label, context):
        """
        Returns a dictionary with the format identifier as the key. The values are
        are fully rendered templates with the given context.
        """
        # conditionally turn off autoescaping for .txt extensions in format
        if format.endswith(".txt"):
            context.autoescape = False

        format_template = render_to_string((
            "notifications/{0}/{1}".format(label, format),
            "notifications/{0}".format(format)), context_instance=context)
        return format_template

    def default_context(self):
        use_ssl = getattr(settings, "USE_SSL", False)
        default_http_protocol = "https" if use_ssl else "http"
        current_site = Site.objects.get_current()
        base_url = "{0}://{1}".format(default_http_protocol, current_site.domain)
        return Context({
            "default_http_protocol": default_http_protocol,
            "current_site": current_site,
            "base_url": base_url
        })
