ROOT_URLCONF = 'notifications.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db',
    }
}

EMAIL_BACKEND = 'django.core.email.backends.locmem.EmailBackend'

SECRET_KEY = 'fake-key'

INSTALLED_APPS=[
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'notifications',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
