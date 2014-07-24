#***********************************************************************************#

# ROUNDWARE
# a contributory, location-aware media platform

# Copyright (C) 2008-2014 Halsey Solutions, LLC
# with contributions from:
# Mike MacHenry, Ben McAllister, Jule Slootbeek and Halsey Burgund (halseyburgund.com)
# http://roundware.org | contact@roundware.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/lgpl.html>.

#***********************************************************************************#


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
