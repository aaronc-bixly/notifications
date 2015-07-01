# Notifications

[![Build Status](https://travis-ci.org/aaronc-bixly/notifications.svg?branch=master)](https://travis-ci.org/aaronc-bixly/notifications)
[![Code Climate](https://codeclimate.com/github/aaronc-bixly/notifications/badges/gpa.svg)](https://codeclimate.com/github/aaronc-bixly/notifications)


This django application allows for notification types to be created and then sent in one command.

This includes:

* Submission of notification messages by other apps
* Notification messages on signing in
* Notification messages via email (configurable by user)
* Ability to supply your own backends notification channels


## Quickstart

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
