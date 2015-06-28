pinax-notifications
===================

This app was originally named `django-notification` but was renamed to
bring a common package name like `notification` under the `pinax` namespace
to avoid conflicts with other like named packages.

In addition, we wanted to take the opportunity to rename it to the plural
form, `notifications` to be in line with the convention we've adopted
across the ecosystem.

This app was developed as part of the Pinax ecosystem but is just a Django app
and can be used independently of other Pinax apps.

To learn more about Pinax, see http://pinaxproject.com/


.. image:: https://travis-ci.org/aaronc-bixly/notifications.svg?branch=master
    :target: https://travis-ci.org/aaronc-bixly/notifications


Many sites need to notify users when certain events have occurred and to allow
configurable options as to how those notifications are to be received.

The project aims to provide a Django app for this sort of functionality. This
includes:

* Submission of notification messages by other apps
* Notification messages on signing in
* Notification messages via email (configurable by user)
* Ability to supply your own backends notification channels


Running the Tests
------------------------------------

::

    $ pip install detox
    $ detox
