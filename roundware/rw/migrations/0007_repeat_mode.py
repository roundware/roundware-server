# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_continuous_spelling(apps, schema_editor):
    """
    Convert all project.repeat_mode values of "continous" to "continuous"
    """

    Project = apps.get_model("rw", "project")
    for project in Project.objects.all():
        if project.repeat_mode == "continous":
            project.repeat_mode = "continuous"
        project.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0006_tag_filter_browse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='repeat_mode',
            field=models.CharField(default='stop', max_length=10, choices=[('stop', 'stop'), ('continuous', 'continuous')]),
        ),
        migrations.RunPython(update_continuous_spelling)
    ]
