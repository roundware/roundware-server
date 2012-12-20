# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ActionNotification.active'
        db.add_column('notifications_actionnotification', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'ModelNotification.active'
        db.add_column('notifications_modelnotification', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ActionNotification.active'
        db.delete_column('notifications_actionnotification', 'active')

        # Deleting field 'ModelNotification.active'
        db.delete_column('notifications_modelnotification', 'active')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'notifications.actionnotification': {
            'Meta': {'object_name': 'ActionNotification'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_sent_reference': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'last_sent_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 12, 13, 0, 0)', 'null': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['notifications.ModelNotification']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'who': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notifications'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'notifications.modelnotification': {
            'Meta': {'object_name': 'ModelNotification'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.IntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Project']"})
        },
        'rw.language': {
            'Meta': {'object_name': 'Language'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'rw.localizedstring': {
            'Meta': {'object_name': 'LocalizedString'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Language']"}),
            'localized_string': ('django.db.models.fields.TextField', [], {})
        },
        'rw.project': {
            'Meta': {'object_name': 'Project'},
            'audio_format': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'auto_submit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'geo_listen_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'geo_speak_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'legal_agreement': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'legal_agreement_loc': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'legal_agreement_string'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rw.LocalizedString']"}),
            'listen_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'listen_questions_dynamic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'max_recording_length': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'new_recording_email_body': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'new_recording_email_recipient': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'out_of_range_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'out_of_range_message_loc': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'out_of_range_msg_string'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rw.LocalizedString']"}),
            'out_of_range_url': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'recording_radius': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'repeat_mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.RepeatMode']", 'null': 'True'}),
            'reset_tag_defaults_on_startup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sharing_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sharing_message_loc': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'sharing_msg_string'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rw.LocalizedString']"}),
            'sharing_url': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'speak_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'speak_questions_dynamic': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'rw.repeatmode': {
            'Meta': {'object_name': 'RepeatMode'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['notifications']