# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0007_add_rate_vote_type'),
        ('rw', '0007_repeat_mode'),
        ('rw', '0008_add_rate_vote_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='timed_asset_priority',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
