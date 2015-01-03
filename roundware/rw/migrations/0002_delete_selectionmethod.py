# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def select_foreign_to_char(apps, schema_editor):
    """
    Convert all MasterUI.select foreign key data to char
    values so the SelectionMethod Table can be dropped.

    Original database table:
    mysql> select * from rw_selectionmethod;
    +----+--------------------+------+
    | id | name               | data |
    +----+--------------------+------+
    |  1 | single             |      |
    |  2 | multi              |      |
    |  3 | multi_at_least_one |      |
    +----+--------------------+------+
    3 rows in set (0.00 sec)
    """
    SINGLE = 'SI'
    MULTI = 'MU'
    MULTI_MIN_ONE = 'MO'

    values = {1: SINGLE,
              2: MULTI,
              3: MULTI_MIN_ONE,
              }

    MasterUI = apps.get_model("rw", "MasterUI")
    for masterui in MasterUI.objects.all():
        masterui.select_new = values[masterui.select.id]
        masterui.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EventType',
        ),
        migrations.AddField(
            model_name='masterui',
            name='select_new',
            field=models.CharField(default='SI',
                                   max_length=2,
                                   choices=[('SI', 'single'),
                                            ('MU', 'multi'),
                                            ('MO', 'multi_at_least_one')]),
            preserve_default=True,
        ),
        migrations.RunPython(select_foreign_to_char),
        migrations.RemoveField(
            model_name='masterui',
            name='select',
        ),
        migrations.RenameField(
            model_name='masterui',
            old_name='select_new',
            new_name='select',
        ),
        migrations.DeleteModel(
            name='SelectionMethod',
        ),
    ]
