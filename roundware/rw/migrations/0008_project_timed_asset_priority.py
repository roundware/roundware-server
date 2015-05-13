# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0007_repeat_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='timed_asset_priority',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
