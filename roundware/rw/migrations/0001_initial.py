# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Language'
        db.create_table('rw_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('rw', ['Language'])

        # Adding model 'LocalizedString'
        db.create_table('rw_localizedstring', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('localized_string', self.gf('django.db.models.fields.TextField')()),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Language'])),
        ))
        db.send_create_signal('rw', ['LocalizedString'])

        # Adding model 'RepeatMode'
        db.create_table('rw_repeatmode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mode', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('rw', ['RepeatMode'])

        # Adding model 'Project'
        db.create_table('rw_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('audio_format', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('auto_submit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('max_recording_length', self.gf('django.db.models.fields.IntegerField')()),
            ('listen_questions_dynamic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('speak_questions_dynamic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sharing_url', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('sharing_message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('out_of_range_message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('out_of_range_url', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('recording_radius', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('listen_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('geo_listen_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('speak_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('geo_speak_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reset_tag_defaults_on_startup', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('legal_agreement', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('new_recording_email_body', self.gf('django.db.models.fields.TextField')(null=True)),
            ('new_recording_email_recipient', self.gf('django.db.models.fields.TextField')(null=True)),
            ('repeat_mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.RepeatMode'], null=True)),
        ))
        db.send_create_signal('rw', ['Project'])

        # Adding M2M table for field sharing_message_loc on 'Project'
        db.create_table('rw_project_sharing_message_loc', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['rw.project'], null=False)),
            ('localizedstring', models.ForeignKey(orm['rw.localizedstring'], null=False))
        ))
        db.create_unique('rw_project_sharing_message_loc', ['project_id', 'localizedstring_id'])

        # Adding M2M table for field out_of_range_message_loc on 'Project'
        db.create_table('rw_project_out_of_range_message_loc', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['rw.project'], null=False)),
            ('localizedstring', models.ForeignKey(orm['rw.localizedstring'], null=False))
        ))
        db.create_unique('rw_project_out_of_range_message_loc', ['project_id', 'localizedstring_id'])

        # Adding M2M table for field legal_agreement_loc on 'Project'
        db.create_table('rw_project_legal_agreement_loc', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['rw.project'], null=False)),
            ('localizedstring', models.ForeignKey(orm['rw.localizedstring'], null=False))
        ))
        db.create_unique('rw_project_legal_agreement_loc', ['project_id', 'localizedstring_id'])

        # Adding model 'Session'
        db.create_table('rw_session', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_id', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('starttime', self.gf('django.db.models.fields.DateTimeField')()),
            ('stoptime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Project'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Language'], null=True)),
            ('client_type', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('client_system', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('rw', ['Session'])

        # Adding model 'UIMode'
        db.create_table('rw_uimode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('rw', ['UIMode'])

        # Adding model 'TagCategory'
        db.create_table('rw_tagcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('rw', ['TagCategory'])

        # Adding model 'SelectionMethod'
        db.create_table('rw_selectionmethod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('rw', ['SelectionMethod'])

        # Adding model 'Tag'
        db.create_table('rw_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.TagCategory'])),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('rw', ['Tag'])

        # Adding M2M table for field loc_msg on 'Tag'
        db.create_table('rw_tag_loc_msg', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tag', models.ForeignKey(orm['rw.tag'], null=False)),
            ('localizedstring', models.ForeignKey(orm['rw.localizedstring'], null=False))
        ))
        db.create_unique('rw_tag_loc_msg', ['tag_id', 'localizedstring_id'])

        # Adding model 'MasterUI'
        db.create_table('rw_masterui', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ui_mode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.UIMode'])),
            ('tag_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.TagCategory'])),
            ('select', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.SelectionMethod'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Project'])),
        ))
        db.send_create_signal('rw', ['MasterUI'])

        # Adding model 'UIMapping'
        db.create_table('rw_uimapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('master_ui', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.MasterUI'])),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Tag'])),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('rw', ['UIMapping'])

        # Adding model 'Audiotrack'
        db.create_table('rw_audiotrack', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Project'])),
            ('minvolume', self.gf('django.db.models.fields.FloatField')()),
            ('maxvolume', self.gf('django.db.models.fields.FloatField')()),
            ('minduration', self.gf('django.db.models.fields.FloatField')()),
            ('maxduration', self.gf('django.db.models.fields.FloatField')()),
            ('mindeadair', self.gf('django.db.models.fields.FloatField')()),
            ('maxdeadair', self.gf('django.db.models.fields.FloatField')()),
            ('minfadeintime', self.gf('django.db.models.fields.FloatField')()),
            ('maxfadeintime', self.gf('django.db.models.fields.FloatField')()),
            ('minfadeouttime', self.gf('django.db.models.fields.FloatField')()),
            ('maxfadeouttime', self.gf('django.db.models.fields.FloatField')()),
            ('minpanpos', self.gf('django.db.models.fields.FloatField')()),
            ('maxpanpos', self.gf('django.db.models.fields.FloatField')()),
            ('minpanduration', self.gf('django.db.models.fields.FloatField')()),
            ('maxpanduration', self.gf('django.db.models.fields.FloatField')()),
            ('repeatrecordings', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('rw', ['Audiotrack'])

        # Adding model 'EventType'
        db.create_table('rw_eventtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('rw', ['EventType'])

        # Adding model 'Event'
        db.create_table('rw_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('client_time', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Session'])),
            ('event_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('tags', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('operationid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('udid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('rw', ['Event'])

        # Adding model 'Asset'
        db.create_table('rw_asset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Session'], null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('volume', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('submitted', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Project'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('audiolength', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Language'], null=True)),
        ))
        db.send_create_signal('rw', ['Asset'])

        # Adding M2M table for field tags on 'Asset'
        db.create_table('rw_asset_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('asset', models.ForeignKey(orm['rw.asset'], null=False)),
            ('tag', models.ForeignKey(orm['rw.tag'], null=False))
        ))
        db.create_unique('rw_asset_tags', ['asset_id', 'tag_id'])

        # Adding model 'Envelope'
        db.create_table('rw_envelope', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Session'])),
        ))
        db.send_create_signal('rw', ['Envelope'])

        # Adding M2M table for field assets on 'Envelope'
        db.create_table('rw_envelope_assets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('envelope', models.ForeignKey(orm['rw.envelope'], null=False)),
            ('asset', models.ForeignKey(orm['rw.asset'], null=False))
        ))
        db.create_unique('rw_envelope_assets', ['envelope_id', 'asset_id'])

        # Adding model 'Speaker'
        db.create_table('rw_speaker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Project'])),
            ('activeyn', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('maxdistance', self.gf('django.db.models.fields.IntegerField')()),
            ('mindistance', self.gf('django.db.models.fields.IntegerField')()),
            ('maxvolume', self.gf('django.db.models.fields.FloatField')()),
            ('minvolume', self.gf('django.db.models.fields.FloatField')()),
            ('uri', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('backupuri', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('rw', ['Speaker'])

        # Adding model 'ListeningHistoryItem'
        db.create_table('rw_listeninghistoryitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Session'])),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Asset'])),
            ('starttime', self.gf('django.db.models.fields.DateTimeField')()),
            ('duration', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('rw', ['ListeningHistoryItem'])

        # Adding model 'Vote'
        db.create_table('rw_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Session'])),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rw.Asset'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('rw', ['Vote'])


    def backwards(self, orm):
        # Deleting model 'Language'
        db.delete_table('rw_language')

        # Deleting model 'LocalizedString'
        db.delete_table('rw_localizedstring')

        # Deleting model 'RepeatMode'
        db.delete_table('rw_repeatmode')

        # Deleting model 'Project'
        db.delete_table('rw_project')

        # Removing M2M table for field sharing_message_loc on 'Project'
        db.delete_table('rw_project_sharing_message_loc')

        # Removing M2M table for field out_of_range_message_loc on 'Project'
        db.delete_table('rw_project_out_of_range_message_loc')

        # Removing M2M table for field legal_agreement_loc on 'Project'
        db.delete_table('rw_project_legal_agreement_loc')

        # Deleting model 'Session'
        db.delete_table('rw_session')

        # Deleting model 'UIMode'
        db.delete_table('rw_uimode')

        # Deleting model 'TagCategory'
        db.delete_table('rw_tagcategory')

        # Deleting model 'SelectionMethod'
        db.delete_table('rw_selectionmethod')

        # Deleting model 'Tag'
        db.delete_table('rw_tag')

        # Removing M2M table for field loc_msg on 'Tag'
        db.delete_table('rw_tag_loc_msg')

        # Deleting model 'MasterUI'
        db.delete_table('rw_masterui')

        # Deleting model 'UIMapping'
        db.delete_table('rw_uimapping')

        # Deleting model 'Audiotrack'
        db.delete_table('rw_audiotrack')

        # Deleting model 'EventType'
        db.delete_table('rw_eventtype')

        # Deleting model 'Event'
        db.delete_table('rw_event')

        # Deleting model 'Asset'
        db.delete_table('rw_asset')

        # Removing M2M table for field tags on 'Asset'
        db.delete_table('rw_asset_tags')

        # Deleting model 'Envelope'
        db.delete_table('rw_envelope')

        # Removing M2M table for field assets on 'Envelope'
        db.delete_table('rw_envelope_assets')

        # Deleting model 'Speaker'
        db.delete_table('rw_speaker')

        # Deleting model 'ListeningHistoryItem'
        db.delete_table('rw_listeninghistoryitem')

        # Deleting model 'Vote'
        db.delete_table('rw_vote')


    models = {
        'rw.asset': {
            'Meta': {'object_name': 'Asset'},
            'audiolength': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Language']", 'null': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Project']", 'null': 'True', 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rw.Session']", 'null': 'True', 'blank': 'True'}),
            'submitted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['rw.Tag']", 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
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