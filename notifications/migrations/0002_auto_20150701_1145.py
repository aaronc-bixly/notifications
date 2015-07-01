# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='noticedigest',
            name='notice_types',
        ),
        migrations.RemoveField(
            model_name='noticedigest',
            name='subscribers',
        ),
        migrations.DeleteModel(
            name='NoticeDigest',
        ),
    ]
