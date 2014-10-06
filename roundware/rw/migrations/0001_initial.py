# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.files.storage
import validatedfile.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('filename', models.CharField(max_length=256, null=True, blank=True)),
                ('file', validatedfile.fields.ValidatedFileField(help_text='Upload file', storage=django.core.files.storage.FileSystemStorage(base_url='/rwmedia/', location='/var/www/roundware/rwmedia/'), upload_to='.')),
                ('volume', models.FloatField(default=1.0, null=True, blank=True)),
                ('submitted', models.BooleanField(default=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('audiolength', models.BigIntegerField(null=True, blank=True)),
                ('weight', models.IntegerField(default=50, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('mediatype', models.CharField(default='audio', max_length=16, choices=[('audio', 'audio'), ('video', 'video'), ('photo', 'photo'), ('text', 'text')])),
                ('description', models.TextField(max_length=2048, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Audiotrack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('minvolume', models.FloatField()),
                ('maxvolume', models.FloatField()),
                ('minduration', models.FloatField()),
                ('maxduration', models.FloatField()),
                ('mindeadair', models.FloatField()),
                ('maxdeadair', models.FloatField()),
                ('minfadeintime', models.FloatField()),
                ('maxfadeintime', models.FloatField()),
                ('minfadeouttime', models.FloatField()),
                ('maxfadeouttime', models.FloatField()),
                ('minpanpos', models.FloatField()),
                ('maxpanpos', models.FloatField()),
                ('minpanduration', models.FloatField()),
                ('maxpanduration', models.FloatField()),
                ('repeatrecordings', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Envelope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
                ('assets', models.ManyToManyField(to='rw.Asset', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server_time', models.DateTimeField()),
                ('client_time', models.CharField(max_length=50, null=True, blank=True)),
                ('event_type', models.CharField(max_length=50)),
                ('data', models.TextField(null=True, blank=True)),
                ('latitude', models.CharField(max_length=50, null=True, blank=True)),
                ('longitude', models.CharField(max_length=50, null=True, blank=True)),
                ('tags', models.TextField(null=True, blank=True)),
                ('operationid', models.IntegerField(null=True, blank=True)),
                ('udid', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ListeningHistoryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('starttime', models.DateTimeField()),
                ('duration', models.BigIntegerField(null=True, blank=True)),
                ('asset', models.ForeignKey(to='rw.Asset')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocalizedString',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('localized_string', models.TextField()),
                ('language', models.ForeignKey(to='rw.Language')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MasterUI',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('active', models.BooleanField(default=True)),
                ('index', models.IntegerField()),
                ('header_text_loc', models.ManyToManyField(to='rw.LocalizedString', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('audio_format', models.CharField(max_length=50)),
                ('auto_submit', models.BooleanField(default=False)),
                ('max_recording_length', models.IntegerField()),
                ('listen_questions_dynamic', models.BooleanField(default=False)),
                ('speak_questions_dynamic', models.BooleanField(default=False)),
                ('sharing_url', models.CharField(max_length=512)),
                ('out_of_range_url', models.CharField(max_length=512)),
                ('recording_radius', models.IntegerField(null=True)),
                ('listen_enabled', models.BooleanField(default=False)),
                ('geo_listen_enabled', models.BooleanField(default=False)),
                ('speak_enabled', models.BooleanField(default=False)),
                ('geo_speak_enabled', models.BooleanField(default=False)),
                ('reset_tag_defaults_on_startup', models.BooleanField(default=False)),
                ('files_url', models.CharField(max_length=512, blank=True)),
                ('files_version', models.CharField(max_length=16, blank=True)),
                ('audio_stream_bitrate', models.CharField(default='128', max_length=3, choices=[('64', '64'), ('96', '96'), ('112', '112'), ('128', '128'), ('160', '160'), ('192', '192'), ('256', '256'), ('320', '320')])),
                ('ordering', models.CharField(default='random', max_length=16, choices=[('by_like', 'by_like'), ('by_weight', 'by_weight'), ('random', 'random')])),
                ('demo_stream_enabled', models.BooleanField(default=False)),
                ('demo_stream_url', models.CharField(max_length=512, blank=True)),
                ('demo_stream_message_loc', models.ManyToManyField(related_name='demo_stream_msg_string', null=True, to='rw.LocalizedString', blank=True)),
                ('legal_agreement_loc', models.ManyToManyField(related_name='legal_agreement_string', null=True, to='rw.LocalizedString', blank=True)),
                ('out_of_range_message_loc', models.ManyToManyField(related_name='out_of_range_msg_string', null=True, to='rw.LocalizedString', blank=True)),
            ],
            options={
                'permissions': (('access_project', 'Access Project'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RepeatMode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mode', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SelectionMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('data', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_id', models.CharField(max_length=36, null=True, blank=True)),
                ('starttime', models.DateTimeField()),
                ('stoptime', models.DateTimeField(null=True, blank=True)),
                ('client_type', models.CharField(max_length=128, null=True, blank=True)),
                ('client_system', models.CharField(max_length=128, null=True, blank=True)),
                ('demo_stream_enabled', models.BooleanField(default=False)),
                ('language', models.ForeignKey(to='rw.Language', null=True)),
                ('project', models.ForeignKey(to='rw.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activeyn', models.BooleanField(default=False)),
                ('code', models.CharField(max_length=10)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('maxdistance', models.IntegerField()),
                ('mindistance', models.IntegerField()),
                ('maxvolume', models.FloatField()),
                ('minvolume', models.FloatField()),
                ('uri', models.URLField()),
                ('backupuri', models.URLField()),
                ('project', models.ForeignKey(to='rw.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
                ('description', models.TextField()),
                ('data', models.TextField(null=True, blank=True)),
                ('filter', models.CharField(default='--', max_length=255, choices=[('--', 'No filter'), ('_within_10km', 'Assets within 10km.'), ('_ten_most_recent_days', 'Assets created within 10 days.')])),
                ('loc_description', models.ManyToManyField(related_name='tag_desc', null=True, to='rw.LocalizedString', blank=True)),
                ('loc_msg', models.ManyToManyField(to='rw.LocalizedString', null=True, blank=True)),
                ('relationships', models.ManyToManyField(related_name='relationships_rel_+', null=True, to='rw.Tag', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('data', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UIMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField()),
                ('default', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('master_ui', models.ForeignKey(to='rw.MasterUI')),
                ('tag', models.ForeignKey(to='rw.Tag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UIMode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('data', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField(null=True, blank=True)),
                ('type', models.CharField(max_length=16, choices=[('like', 'like'), ('flag', 'flag')])),
                ('asset', models.ForeignKey(to='rw.Asset')),
                ('session', models.ForeignKey(to='rw.Session')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tag',
            name='tag_category',
            field=models.ForeignKey(to='rw.TagCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='repeat_mode',
            field=models.ForeignKey(to='rw.RepeatMode', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='sharing_message_loc',
            field=models.ManyToManyField(related_name='sharing_msg_string', null=True, to='rw.LocalizedString', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterui',
            name='project',
            field=models.ForeignKey(to='rw.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterui',
            name='select',
            field=models.ForeignKey(to='rw.SelectionMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterui',
            name='tag_category',
            field=models.ForeignKey(to='rw.TagCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterui',
            name='ui_mode',
            field=models.ForeignKey(to='rw.UIMode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='listeninghistoryitem',
            name='session',
            field=models.ForeignKey(to='rw.Session'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='session',
            field=models.ForeignKey(to='rw.Session'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='envelope',
            name='session',
            field=models.ForeignKey(to='rw.Session', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='audiotrack',
            name='project',
            field=models.ForeignKey(to='rw.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='initialenvelope',
            field=models.ForeignKey(to='rw.Envelope', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='language',
            field=models.ForeignKey(to='rw.Language', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='loc_description',
            field=models.ManyToManyField(to='rw.LocalizedString', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='project',
            field=models.ForeignKey(to='rw.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='session',
            field=models.ForeignKey(blank=True, to='rw.Session', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='tags',
            field=models.ManyToManyField(to='rw.Tag', null=True, blank=True),
            preserve_default=True,
        ),
    ]
