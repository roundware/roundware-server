# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-04-18 17:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0028_add_uielement_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='envelope',
            name='assets',
            field=models.ManyToManyField(blank=True, related_name='envelope', to='rw.Asset'),
        ),
    ]
