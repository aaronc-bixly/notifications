# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoticeHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.TextField()),
                ('extra_context', models.TextField()),
                ('sent', models.DateTimeField(editable=False)),
                ('notice_type', models.ForeignKey(to='notifications.NoticeType')),
            ],
        ),
        migrations.CreateModel(
            name='NoticeThrough',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('history', models.ForeignKey(to='notifications.NoticeHistory')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='noticequeuebatch',
            name='send_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='noticehistory',
            name='recipient',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='notifications.NoticeThrough'),
        ),
    ]
