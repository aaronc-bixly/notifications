# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20150701_1145'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='noticehistory',
            options={'verbose_name': 'Notice History', 'verbose_name_plural': 'Notice History'},
        ),
        migrations.AlterModelOptions(
            name='noticesetting',
            options={'verbose_name': 'Notice Setting', 'verbose_name_plural': 'Notice Settings'},
        ),
        migrations.AlterModelOptions(
            name='noticetype',
            options={'verbose_name': 'Notice Type', 'verbose_name_plural': 'Notice Types'},
        ),
    ]
