# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0009_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='timezone',
            field=models.CharField(default='0000', max_length=5),
            preserve_default=True,
        ),
    ]
