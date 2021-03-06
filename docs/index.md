# notifications

This django application allows for notification types to be created and then sent in one command.

This includes:

* Submission of notification messages by other apps
* Notification messages on signing in
* Notification messages via email (configurable by user)
* Ability to supply your own backends notification channels


## Quickstart

To install, simply download the tar.gz and use pip install:

    pip install notifications-0.1.1.tar.gz


Add `notifications` to your `INSTALLED_APPS` setting:

    INSTALLED_APPS = (
        # ...
        "notifications",
        # ...
    )

Create one or more notice types:

    from notifications.models import NoticeType
    NoticeType.create(label, display, description)

In your code, send events;

    from notifications.models import send_now
    send_now([users], "label", {"extra": context})

