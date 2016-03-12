# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ('rw', '0012_asset_ordering'),
    ]

    operations = [
        migrations.AddField(
                model_name='project',
                name='out_of_range_distance',
                field=models.FloatField(default=1000),
                preserve_default=True,
        ),
        migrations.AddField(
                model_name='speaker',
                name='attenuation_border',
                field=django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True, editable=False,
                                                                        geography=True),
                preserve_default=True,
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
                field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, geography=True),
                preserve_default=True,
        ),
        migrations.AlterField(
                model_name='speaker',
                name='latitude',
                field=models.FloatField(null=True),
                preserve_default=True,
        ),
        migrations.AlterField(
                model_name='speaker',
                name='longitude',
                field=models.FloatField(null=True),
                preserve_default=True,
        ),
        migrations.AlterField(
                model_name='speaker',
                name='maxdistance',
                field=models.IntegerField(null=True),
                preserve_default=True,
        ),
        migrations.AlterField(
                model_name='speaker',
                name='mindistance',
                field=models.IntegerField(null=True),
                preserve_default=True,
        ),
    ]
