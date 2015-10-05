# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0010_session_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='type',
            field=models.CharField(max_length=16, choices=[('like', 'like'), ('flag', 'flag'), ('rate', 'rate')]),
        ),
    ]
