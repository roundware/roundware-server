# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
from roundware.rw.fields import ValidatedFileField


class Migration(migrations.Migration):

    dependencies = [
        ('rw', '0015_remove_null_from_mtm'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rw.TagRelationship')),
            ],
        ),
        migrations.AddField(
            model_name='asset',
            name='loc_alt_text',
            field=models.ManyToManyField(blank=True, related_name='alt_text_string', to='rw.LocalizedString'),
        ),
        migrations.AddField(
            model_name='tag',
            name='location',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(geography=True, null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='tag',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rw.Project'),
        ),
        migrations.AddField(
            model_name='tagrelationship',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rw.Tag'),
        ),
        migrations.RenameModel('MasterUI', 'UIGroup'),
        migrations.RenameModel('UIMapping', 'UIItem'),
        migrations.RenameField(
            model_name='uiitem',
            old_name='master_ui',
            new_name='ui_group',
        ),
        migrations.AddField(
            model_name='asset',
            name='loc_caption',
            field=ValidatedFileField(help_text='Upload captions', null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/rwmedia/', location='/var/www/roundware/rwmedia/'), upload_to='.'),
        ),
        migrations.AddField(
            model_name='uiitem',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rw.UIItem'),
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='relationships',
            new_name='relationships_old'
        ),
        migrations.AlterField(
            model_name='tag',
            name='location',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, geography=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='tagrelationship',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rw.TagRelationship'),
        ),
    ]
