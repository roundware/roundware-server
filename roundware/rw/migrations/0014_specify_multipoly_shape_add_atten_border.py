# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ('rw', '0013_allow_null_in_deprecated_fields'),
    ]

    operations = [
        migrations.AddField(
                model_name='speaker',
                name='attenuation_border',
                field=django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True, editable=False,
                                                                        geography=True),
                preserve_default=True,
        ),
        migrations.AlterField(
                model_name='speaker',
                name='shape',
                field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, geography=True),
                preserve_default=True,
        ),
    ]
