# Usage

Integrating notification support into your app is a simple three-step process:

1. Create your notice types
2. Create your notice templates
3. Send notifications


## Creating Notice Types

You need to call `NoticeType.create(label, display, description, assets)` once to
create the notice types for your application in the database where:
* `label` is just the internal short name that will be used for the type
* `display` is what the user will see as the name of the notification type
* `description` is a short description
* `assets` is optional, and will take a list of files located in `static/notifications`. This variable is used if your
    notice type will use any images in its email.

For example:

    from pinax.notifications.models import NoticeType
    
    NoticeType.create(
        "friends_invite",
        "Invitation Received",
        "you have received an invitation",
        ["footer.png"]
    )
    
In Django 1.7-1.8, you can attach the creation of these to the `post_migrate` signal,
so that your NoticeTypes are always there, even when the database is reset. You can 
use this in the apps that require their own NoticeTypes

    # myapp/apps.py
    from django.apps import AppConfig
    from django.db.models.signals import post_migrate
    
    from notifications.models import NoticeType

    create_notice_types(sender, **kwargs):
        NoticeType.create(....)
        pass

    class MyAppConfig(AppConfig):
        name = 'myapp'
        verbose_name = 'My App'
    
        def ready(self):
            post_migrate.connect(create_notice_types, sender=self)

Examples of how to use `post_migrate` can be found in the [Django Docs](https://docs.djangoproject.com/en/1.7/ref/signals/#post-migrate).

This will call the handler to create notices after the application is migrated.

    # myapp/__init__.py
    default_app_config = 'myapp.apps.MyAppConfig'

## Notification Templates

To use the assets you placed in the NoticeType, call on them using `cid:`, followed by the file name. For example, if
you passed "footer.png" into your NoticeType.create, and you have "footer.png" located in
`<your_static_folder>/notifications/footer.png`, then you can insert the image into the template using the line
`<img src="cid:footer.png">`.


### Backends

Using templates with the email backend is very simple. The email backend uses three templates:
* `email_subject.txt` - Used to render the subject line of the email.
* `email_body.html` - Used to render the body of the email.
* `digest.html` - Used to render a digest of notifications.

This templates are very basic, though, so you are encouraged to create your own templates.
Any django template will work, and to do this, simply place the templates in 
`notifications/<notice_type_label>/<template_name>`

If you used the following code to create a NoticeType:

    NoticeType.create("MyAppLabel", "A label for MyApp", "This is the description")
then your custom template for the email body would be placed in `notifications/MyAppLabel/email_body.html`

In addition to the extra context that is supplied via the `send` call in your site or app, these templates are
rendered with the following context variables:

* `default_http_protocol` - `https` if `settings.USE_SSL` is True, otherwise `http`
* `current_site` - `Site.objects.get_current()`
* `base_url` - the default http protocol combined with the current site domain
* `recipient_email` - the email that will receive the notice
* `sender` - the value supplied to the `sender` kwarg of the `send` method (often this is not set and will be default to
 the `DEFAULT_FROM_EMAIL` setting in your `settings.py`)
* `notice` - display value of the notice type


## Sending Notifications

There are two different ways of sending out notifications. We have support for blocking and non-blocking methods of
sending notifications. The most simple way to send out a notification, for example:

    send([to_user], "friends_invite", {"from_user": from_user})

One thing to note is that `send` is a proxy around either `send_now` or
`queue`. They all have the same signature.



### `send` vs. `queue` vs. `send_now`

Lets first break down what each does.

#### `send`

    send(users, label, extra_context, sender, attachments, send_at, send, queue)

This is a blocking call that will check each user for elgibility of the
notice and actually peform the send.

The parameters are:

* `users` is an iterable of `User` objects or email strings to send the notification to.
* `label` is the label you used in the previous step to identify the notice type.
* `extra_content` is a dictionary to add custom context entries to the template used to render to notification.
    This is optional. Read about backends to discover what context will be available to you automatically in your
    template.
* `sender` is the email address that will be used when sending the email. This is optional.
* `attachments` is a list of the absolute path to an attachment you want added to your email notification.
* `send`, if set to `True`, will send the notification immediately to `users`. Defaults to `False`.
* `queue`, if set to `True`, will queue the notification for later use. Defaults to `False`.
* `send_at` will set a time for when the queued notification can be sent. If not set, the queued notification will
   be sent whenever the `emit-notices` command is called.

Special note, send will not work if both `send` and `queue` are both `True`, so choose or the other or neither.
If both are `False`, the behavior will come from `NOTIFICATIONS_QUEUE_ALL` in your `settings.py`, which will default to
`False` if not set.

#### `queue`

    queue(users, label, extra_context, sender, attachments, send_at)

This is a non-blocking call that will queue the call to `send_now` to be executed at a later time. To later execute
the call you need to use the `emit_notices` management command.

Parameters are the same as `send_now`, excluding send and queue.


#### `send_now`

    send_now(users, label, extra_context, sender, attachments)
    
This is a blocking call that will automatically send the notification using the backend set.

Parameters are the same as `send_now`, excluding send and queue.

