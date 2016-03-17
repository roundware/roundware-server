# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def ui_mode_foreign_to_char(apps, schema_editor):
    """
    Convert all MasterUI.ui_mode foreign key data to char values so the
    UIMode Table can be dropped.

    Original database table:
    mysql> select * from rw_uimode;
    +----+--------+------+
    | id | name   | data |
    +----+--------+------+
    |  1 | listen |      |
    |  2 | speak  |      |
    +----+--------+------+
    2 rows in set (0.00 sec)
    """
    LISTEN = 'listen'
    SPEAK = 'speak'

    values = {1: LISTEN,
              2: SPEAK, }

    MasterUI = apps.get_model("rw", "MasterUI")
    for masterui in MasterUI.objects.all():
        masterui.ui_mode_new = values[masterui.ui_mode.id]
        masterui.save()

class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0002_select_method_to_choice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='operationid',
        ),
        migrations.RemoveField(
            model_name='event',
            name='udid',
        ),
        migrations.AddField(
            model_name='masterui',
            name='ui_mode_new',
            field=models.CharField(default='listen',
                                   max_length=6,
                                   choices=[('listen', 'listen'),
                                            ('speak', 'speak')]),
            preserve_default=True,
        ),
        migrations.RunPython(ui_mode_foreign_to_char),
        migrations.RemoveField(
            model_name='masterui',
            name='ui_mode',
        ),
        migrations.RenameField(
            model_name='masterui',
            old_name='ui_mode_new',
            new_name='ui_mode',
        ),
        migrations.DeleteModel(
            name='UIMode',
        ),
    ]
