# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('rw', '0012_add_speaker_geom_and_attenuation_dist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speaker',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='longitude',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='maxdistance',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='mindistance',
            field=models.IntegerField(null=True),
        ),
    ]
