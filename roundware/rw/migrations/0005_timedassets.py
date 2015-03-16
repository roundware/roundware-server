# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0004_repeat_mode_to_choice'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimedAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.FloatField()),
                ('end', models.FloatField()),
                ('asset', models.ForeignKey(to='rw.Asset')),
                ('project', models.ForeignKey(to='rw.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
