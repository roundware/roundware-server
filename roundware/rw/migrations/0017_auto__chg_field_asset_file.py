# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Asset.file'
        db.alter_column('rw_asset', 'file', self.gf('roundware.rw.fields.RWValidatedFileField')(max_length=100, null=True))

    def backwards(self, orm):

        # Changing field 'Asset.file'
        db.alter_column('rw_asset', 'file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True))

    models = {
        'rw.asset': {
            'Meta': {'object_name': 'Asset'},
            'audiolength': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2048', 'blank': 'True'}),
            'file': ('roundware.rw.fields.RWValidatedFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Language']", 'null': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'mediatype': ('django.db.models.fields.CharField', [], {'default': "'audio'", 'max_length': '16'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Project']", 'null': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Session']", 'null': 'True', 'blank': 'True'}),
            'submitted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['rw.Tag']", 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '50'})
        },
        'rw.audiotrack': {
            'Meta': {'object_name': 'Audiotrack'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maxdeadair': ('django.db.models.fields.FloatField', [], {}),
            'maxduration': ('django.db.models.fields.FloatField', [], {}),
            'maxfadeintime': ('django.db.models.fields.FloatField', [], {}),
            'maxfadeouttime': ('django.db.models.fields.FloatField', [], {}),
            'maxpanduration': ('django.db.models.fields.FloatField', [], {}),
            'maxpanpos': ('django.db.models.fields.FloatField', [], {}),
            'maxvolume': ('django.db.models.fields.FloatField', [], {}),
            'mindeadair': ('django.db.models.fields.FloatField', [], {}),
            'minduration': ('django.db.models.fields.FloatField', [], {}),
            'minfadeintime': ('django.db.models.fields.FloatField', [], {}),
            'minfadeouttime': ('django.db.models.fields.FloatField', [], {}),
            'minpanduration': ('django.db.models.fields.FloatField', [], {}),
            'minpanpos': ('django.db.models.fields.FloatField', [], {}),
            'minvolume': ('django.db.models.fields.FloatField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Project']"}),
            'repeatrecordings': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'rw.envelope': {
            'Meta': {'object_name': 'Envelope'},
            'assets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['rw.Asset']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Session']"})
        },
        'rw.event': {
            'Meta': {'object_name': 'Event'},
            'client_time': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'operationid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'server_time': ('django.db.models.fields.DateTimeField', [], {}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Session']"}),
            'tags': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'udid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'rw.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'rw.language': {
            'Meta': {'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'rw.listeninghistoryitem': {
            'Meta': {'object_name': 'ListeningHistoryItem'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Asset']"}),
            'duration': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Session']"}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {})
        },
        'rw.localizedstring': {
            'Meta': {'object_name': 'LocalizedString'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Language']"}),
            'localized_string': ('django.db.models.fields.TextField', [], {})
        },
        'rw.masterui': {
            'Meta': {'object_name': 'MasterUI'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'header_text_loc': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['rw.LocalizedString']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Project']"}),
            'select': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.SelectionMethod']"}),
            'tag_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.TagCategory']"}),
            'ui_mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.UIMode']"})
        },
        'rw.project': {
            'Meta': {'object_name': 'Project'},
            'audio_format': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'audio_stream_bitrate': ('django.db.models.fields.CharField', [], {'default': "'128'", 'max_length': '3'}),
            'auto_submit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'demo_stream_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'demo_stream_message_loc': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'demo_stream_msg_string'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rw.LocalizedString']"}),
            'demo_stream_url': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'files_url': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'files_version': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'geo_listen_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'geo_speak_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'legal_agreement_loc': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'legal_agreement_string'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rw.LocalizedString']"}),
            'listen_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'listen_questions_dynamic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'max_recording_length': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ordering': ('django.db.models.fields.CharField', [], {'default': "'random'", 'max_length': '16'}),
            'out_of_range_message_loc': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'out_of_range_msg_string'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rw.LocalizedString']"}),
            'out_of_range_url': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'recording_radius': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'repeat_mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.RepeatMode']", 'null': 'True'}),
            'reset_tag_defaults_on_startup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sharing_message_loc': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'sharing_msg_string'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rw.LocalizedString']"}),
            'sharing_url': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'speak_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'speak_questions_dynamic': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'rw.repeatmode': {
            'Meta': {'object_name': 'RepeatMode'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'rw.selectionmethod': {
            'Meta': {'object_name': 'SelectionMethod'},
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'rw.session': {
            'Meta': {'object_name': 'Session'},
            'client_system': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'client_type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'demo_stream_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'device_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Language']", 'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Project']"}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'stoptime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'rw.speaker': {
            'Meta': {'object_name': 'Speaker'},
            'activeyn': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'backupuri': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'maxdistance': ('django.db.models.fields.IntegerField', [], {}),
            'maxvolume': ('django.db.models.fields.FloatField', [], {}),
            'mindistance': ('django.db.models.fields.IntegerField', [], {}),
            'minvolume': ('django.db.models.fields.FloatField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Project']"}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'rw.tag': {
            'Meta': {'object_name': 'Tag'},
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loc_msg': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['rw.LocalizedString']", 'null': 'True', 'blank': 'True'}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'relationships_rel_+'", 'null': 'True', 'to': "orm['rw.Tag']"}),
            'tag_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.TagCategory']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'rw.tagcategory': {
            'Meta': {'object_name': 'TagCategory'},
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'rw.uimapping': {
            'Meta': {'object_name': 'UIMapping'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'master_ui': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.MasterUI']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Tag']"})
        },
        'rw.uimode': {
            'Meta': {'object_name': 'UIMode'},
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'rw.vote': {
            'Meta': {'object_name': 'Vote'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Asset']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Session']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['rw']