# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20150625_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticetype',
            name='assets',
            field=models.TextField(null=True, verbose_name='assets', blank=True),
        ),
    ]
