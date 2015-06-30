# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='language')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NoticeHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender', models.TextField()),
                ('extra_context', models.TextField(null=True, blank=True)),
                ('attachments', models.TextField(null=True, blank=True)),
                ('sent_at', models.DateTimeField(editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NoticeQueueBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pickled_data', models.TextField()),
                ('send_at', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NoticeSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('medium', models.CharField(max_length=1, verbose_name='medium', choices=[(0, 'email')])),
                ('send', models.BooleanField(default=False, verbose_name='send')),
                ('scoping_object_id', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'notice setting',
                'verbose_name_plural': 'notice settings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NoticeThrough',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('history', models.ForeignKey(to='notifications.NoticeHistory')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NoticeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=40, verbose_name='label')),
                ('display', models.CharField(max_length=50, verbose_name='display')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('assets', models.TextField(null=True, verbose_name='assets', blank=True)),
                ('default', models.IntegerField(verbose_name='default')),
            ],
            options={
                'verbose_name': 'notice type',
                'verbose_name_plural': 'notice types',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='noticesetting',
            name='notice_type',
            field=models.ForeignKey(verbose_name='notice type', to='notifications.NoticeType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='noticesetting',
            name='scoping_content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='noticesetting',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='noticesetting',
            unique_together=set([('user', 'notice_type', 'medium', 'scoping_content_type', 'scoping_object_id')]),
        ),
        migrations.AddField(
            model_name='noticehistory',
            name='notice_type',
            field=models.ForeignKey(to='notifications.NoticeType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='noticehistory',
            name='recipient',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='notifications.NoticeThrough'),
            preserve_default=True,
        ),
    ]
