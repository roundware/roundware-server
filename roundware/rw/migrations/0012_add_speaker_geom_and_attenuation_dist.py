# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ('rw', '0011_add_rate_vote_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asset',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='speaker',
            name='attenuation_distance',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='speaker',
            name='boundary',
            field=django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True, editable=False,
                                                                    geography=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='speaker',
            name='shape',
            field=django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True, geography=True),
            preserve_default=True,
        ),
    ]
