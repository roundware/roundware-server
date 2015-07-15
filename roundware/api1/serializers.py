# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from roundware.rw.models import Asset, Project, Event, Session, ListeningHistoryItem
from rest_framework import serializers


class AssetSerializer(serializers.ModelSerializer):
    audiolength_in_seconds = serializers.FloatField()
    class Meta:
        model = Asset


class AssetLocationSerializer(serializers.ModelSerializer):
    resource_uri = serializers.HyperlinkedIdentityField(view_name='api1-assetlocation-detail')
    class Meta:
        model = Asset
        fields = ('project',
                  'latitude',
                  'longitude',
                  'id',
                  'filename',
                  'description',
                  'resource_uri')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session


class ListeningHistoryItemAssetSerializer(serializers.ModelSerializer):
    duration_in_seconds = serializers.FloatField()
    class Meta:
        model = ListeningHistoryItem
