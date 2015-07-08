# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0003_auto_20150702_1236'),
    ]

    operations = [
        migrations.CreateModel(
            name='DigestSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notice_type', models.CharField(max_length=40, verbose_name='notice type')),
                ('emit_at', models.DateTimeField(editable=False)),
                ('frequency', models.PositiveIntegerField(default=604800)),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Digest Subscription',
                'verbose_name_plural': 'Digest Subscriptions',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='noticequeuebatch',
            options={'verbose_name': 'Notice Queue Batch', 'verbose_name_plural': 'Notice Queue Batches'},
        ),
    ]
