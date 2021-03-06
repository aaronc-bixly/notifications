#!/usr/bin/env python
import os
import sys

import django
from django.core.management import call_command
from django.conf import settings
from django.test.utils import get_runner


def runtests():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    call_command("makemigrations")
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1)
    failures = test_runner.run_tests(['tests'])
    sys.exit(bool(failures))

if __name__ == "__main__":
    runtests()
