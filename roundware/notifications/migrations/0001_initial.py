# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('action', models.IntegerField(choices=[(0, 'add'), (1, 'edit'), (2, 'delete')])),
                ('message', models.TextField()),
                ('subject', models.CharField(max_length=255, blank=True)),
                ('last_sent_time', models.DateTimeField(default=datetime.datetime(2014, 10, 2, 20, 17, 56, 428492), null=True)),
                ('last_sent_reference', models.IntegerField(null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModelNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('model', models.IntegerField(choices=[(0, 'Asset')])),
                ('active', models.BooleanField(default=True)),
                ('project', models.ForeignKey(to='rw.Project', on_delete = models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='actionnotification',
            name='notification',
            field=models.ForeignKey(to='notifications.ModelNotification', on_delete = models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actionnotification',
            name='who',
            field=models.ManyToManyField(related_name='notifications', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
