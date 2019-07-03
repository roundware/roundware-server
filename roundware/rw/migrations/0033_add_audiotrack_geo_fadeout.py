# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2019-05-01 22:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0032_add_asset_crop_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='audiotrack',
            options={},
        ),
        migrations.AddField(
            model_name='audiotrack',
            name='fadeout_when_filtered',
            field=models.BooleanField(default=False, verbose_name='Fade Out When Asset Filtered'),
        ),
    ]
