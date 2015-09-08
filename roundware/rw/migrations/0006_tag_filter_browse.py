# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_tag_filter_default(apps, schema_editor):
    """
    Convert all tag.filter values of "--" to ""
    """

    Tag = apps.get_model("rw", "tag")
    for tag in Tag.objects.all():
        if tag.filter == "--":
            tag.filter = None
        tag.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0005_timedassets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterui',
            name='ui_mode',
            field=models.CharField(default='listen', max_length=6, choices=[('listen', 'listen'), ('speak', 'speak'), ('browse', 'browse')]),
        ),
        migrations.AlterField(
            model_name='tag',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='filter',
            field=models.CharField(default='', max_length=255, blank=True, choices=[('', 'No filter'), ('_within_10km', 'Assets within 10km.'), ('_ten_most_recent_days', 'Assets created within 10 days.')]),
        ),
        migrations.RunPython(update_tag_filter_default)
    ]
