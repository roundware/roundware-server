# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('rw', '0011_add_rate_vote_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
                name='asset',
                options={'ordering': ['id']},
        ),
    ]
