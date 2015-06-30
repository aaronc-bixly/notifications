# Settings

The following allows you to specify the behavior of `notifications` in
your project. Please be aware of the native Django settings which can affect
the behavior of `notification`.


## NOTIFICATIONS_BACKENDS

Defaults to:

    [
        ("email", "notifications.backends.email_backend.EmailBackend"),
    ]


## USE_SSL

It defaults to `False`.

This is used to specify the beginning of URLs in the default `email_body.html`
file. A common use-case for overriding this default might be `https` for use on
more secure projects.


## NOTIFICATIONS_LANGUAGE_MODEL

There is not set default for this setting. It allows users to specify their own
notification language.

Example model in a `languages` app::

    from django.conf import settings

    class Language(models.Model):
    
        user = models.ForeignKey(User)
        language = models.CharField(max_length=10, choices=settings.LANGUAGES)


Setting this value in `settings.py`::

    NOTIFICATIONS_LANGUAGE_MODEL = "languages.Language"


DEFAULT_FROM_EMAIL
------------------

Defaults to `webmaster@localhost` and is a [standard Django setting](https://docs.djangoproject.com/en/1.7/ref/settings/#default-from-email).

Default e-mail address to use for various automated correspondence from
`notifications.backends.email`.


## LANGUAGES

Defaults to a tuple of all available languages and is a
[standard Django setting](https://docs.djangoproject.com/en/1.7/ref/settings/#languages).

The default for this is specifically used for things like the Django admin.
However, if you need to specify a subset of languages for your site's front end
you can use this setting to override the default. In which case this is the
definated pattern of usage::

    gettext = lambda s: s

    LANGUAGES = (
        ("en", gettext("English")),
        ("fr", gettext("French")),
    )


## NOTIFICATIONS_QUEUE_ALL

It defaults to `False`.

By default, calling `notification.send` will send the notification immediately,
however, if you set this setting to True, then the default behavior of the
`send` method will be to queue messages in the database for sending via the
`emit_notices` command.


## NOTIFICATIONS_LOCK_WAIT_TIMEOUT

It defaults to `-1`.

It defines how long to wait for the lock to become available. Default of -1
means to never wait for the lock to become available. This only applies when
using crontab setup to execute the `emit_notices` management command to send
queued messages rather than sending immediately.
