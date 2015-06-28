import os
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext
from django.utils.html import strip_tags

from notifications.backends.base import BaseBackend


class EmailBackend(BaseBackend):
    spam_sensitivity = 2

    def can_send(self, user, notice_type, scoping):
        can_send = super(EmailBackend, self).can_send(user, notice_type, scoping)
        if can_send and user.email:
            return True
        return False

    def deliver(self, notice_type, extra_context, attachments, recipient, sender=settings.DEFAULT_FROM_EMAIL):
        # TODO: require this to be passed in extra_context

        context = self.default_context()
        context.update({
            "recipient": recipient,
            "sender": sender,
            "notice": ugettext(notice_type.display),
        })
        context.update(extra_context)

        body = self.get_formatted_message("email_body.html", notice_type.label, context)

        subject = "".join(render_to_string("notifications/email_subject.txt", context).splitlines())

        body_text = strip_tags(body)

        msg = EmailMultiAlternatives(subject, body_text, sender, to=[recipient.email])
        msg.attach_alternative(body, "text/html")
        msg.mixed_subtype = "related"

        assets = notice_type.get_assets()
        for file in assets:
            path = os.path.join(settings.STATIC_ROOT, "notifications", file)
            fp = open(path, 'rb')
            msg_img = MIMEImage(fp.read())
            fp.close()
            msg_img.add_header('Content-ID', '<{}>'.format(file))
            msg.attach(msg_img)

        for attachment in attachments:
            msg.attach_file(attachment)

        msg.send()
