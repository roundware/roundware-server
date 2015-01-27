# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def ui_mode_foreign_to_char(apps, schema_editor):
    """
    Convert all Project.repear_mode foreign key data to char values so the
    RepeatMode Table can be dropped.

    Original database table:
    mysql> select * from rw_repeatmode;
    +----+------------+
    | id | mode       |
    +----+------------+
    |  1 | stop       |
    |  2 | continuous |
    +----+------------+
    2 rows in set (0.00 sec)

    """
    STOP = 'stop'
    CONTINOUS = 'continous'

    values = {1: STOP,
              2: CONTINOUS, }

    Projects = apps.get_model("rw", "Project")
    for project in Projects.objects.all():
        project.repeat_mode_new = values[project.repeat_mode.id]
        project.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0003_uimode_to_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='repeat_mode_new',
            field=models.CharField(default='stop',
                                   max_length=9,
                                   choices=[('stop', 'stop'),
                                            ('continous', 'continous')]),
            preserve_default=True,
        ),
        migrations.RunPython(ui_mode_foreign_to_char),
        migrations.RemoveField(
            model_name='project',
            name='repeat_mode',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='repeat_mode_new',
            new_name='repeat_mode',
        ),
        migrations.DeleteModel(
            name='RepeatMode',
        ),
    ]
