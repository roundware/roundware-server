# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def calculate_attenuation_distance(apps, schema_editor):
    """
    Calculate new attenuation_distance from old min/max distance values
    """
    Speaker = apps.get_model("rw", "speaker")
    for speaker in Speaker.objects.all():
        if not speaker.attenuation_distance:
            speaker.attenuation_distance = speaker.maxdistance - speaker.mindistance
            speaker.save()

def save_speakers(apps, schema_editor):
    """save speakers to generate derivative shapes after updating the `shape` attribute
    """
    Speaker = apps.get_model("rw", "Speaker")
    for speaker in Speaker.objects.all():
        # recalculate the shape boundary
        speaker.boundary = speaker.shape.boundary
        speaker.save()

class Migration(migrations.Migration):
    dependencies = [
        ('rw', '0013_speaker_geometry'),
    ]

    operations = [
        migrations.RunPython(calculate_attenuation_distance),
        migrations.RunSQL(
                # calculate the shape
                "UPDATE rw_speaker SET shape = ST_Multi(ST_Buffer(ST_MakePoint(longitude, latitude)::geography, maxdistance)::geometry)::geography;"
                # calculate the border
                "UPDATE rw_speaker SET attenuation_border = ST_Boundary(ST_Buffer(shape, -attenuation_distance)::geometry)::geography;"
        ),
        migrations.RunPython(save_speakers)
    ]
