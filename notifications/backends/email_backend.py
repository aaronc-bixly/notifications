import os
import re
from email.mime.image import MIMEImage

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import ugettext
from django.utils.html import strip_tags
from django.contrib.sites.models import Site

from notifications.backends.base import BaseBackend
from notifications.conf import settings


class EmailBackend(BaseBackend):
    spam_sensitivity = 2

    def can_send(self, user, notice_type, scoping):
        can_send = super(EmailBackend, self).can_send(user, notice_type, scoping)
        if can_send and user.email:
            return True
        return False

    def deliver(self, notice_type, extra_context, attachments, recipient, sender=settings.DEFAULT_FROM_EMAIL):
        context = self.default_context()
        context.update({
            "recipient": recipient,
            "sender": sender,
            "notice": ugettext(notice_type.display),
        })
        context.update(extra_context)

        subject = "".join(render_to_string("notifications/email_subject.txt", context).splitlines())
        body = self.get_formatted_message("email_body.html", notice_type.label, context)
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


    def render_history(self, notice_history):
        renderings = []
        for notice in notice_history:
            context = self.default_context()
            context.update({
                "recipient": notice.recipient,
                "sender": notice.sender,
                "notice": ugettext(notice.notice_type.display),
            })
            context.update(notice.extra_context)

            email_body = self.get_formatted_message("email_body.html", notice.notice_type.label, context)
            html_body = re.findall(r"<body>\n((?:.+\n)*)</body>", email_body)
            html_body = html_body[0]
            renderings.append((notice, html_body))

        return renderings

    def deliver_digest(self, users, notice_history):
        rendered_history = self.render_history(notice_history)
        digest_body = render_to_string(["notifications/custom/digest.html", "notifications/digest.html"], {'notice_history': rendered_history})
        digest_text = strip_tags(digest_body)
        digest_subject = "Digest from " + Site.objects.get_current().domain

        emails = []
        for user in users:
            emails.append(user.email)

        msg = EmailMultiAlternatives(digest_subject, digest_text, settings.DEFAULT_FROM_EMAIL, bcc=emails)
        msg.attach_alternative(digest_body, "text/html")
        msg.mixed_subtype = "related"

        asset_list = []
        for notice in notice_history:
            asset_list = asset_list + notice.notice_type.get_assets()
        asset_set = set(asset_list)
        for file in asset_set:
            path = os.path.join(settings.STATIC_ROOT, "notifications", file)
            fp = open(path, 'rb')
            msg_img = MIMEImage(fp.read())
            fp.close()
            msg_img.add_header('Content-ID', '<{}>'.format(file))
            msg.attach(msg_img)

        msg.send()
