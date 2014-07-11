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
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from tastypie import fields
from roundware.rw.models import Asset, Project, Event, Session, ListeningHistoryItem
from roundware.rw.serializers import PrettyJSONSerializer


class AssetResource(ModelResource):
    project = fields.IntegerField(attribute="project_id")
    language = fields.IntegerField(attribute="language_id")
    session = fields.IntegerField(attribute="session_id")
    audiolength_in_seconds = fields.FloatField(
        attribute="audiolength_in_seconds")

    class Meta:
        queryset = Asset.objects.all()
        resource_name = "asset"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()
        filtering = {
            "mediatype": ('exact', 'startswith',),
            "submitted": ('exact',),
            "created": ('exact', 'gte', 'lte', 'range'),
            "project": ('exact',),
            "audiolength": ('gte', 'lte'),
            "language": ('exact',),
            "session": ('exact',),
        }


class AssetLocationResource(AssetResource):
    project = fields.IntegerField(attribute="project_id")

    class Meta:
        queryset = Asset.objects.filter()
        resource_name = "assetlocation"
        allowed_methods = ['get', 'patch']
        fields = ['latitude', 'longitude', 'id', 'filename', 'description']
        serializer = PrettyJSONSerializer()
        filtering = {
            'project': ('exact',)
        }
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()


class ProjectResource(ModelResource):

    class Meta:
        queryset = Project.objects.all()
        resource_name = "project"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()


class EventResource(ModelResource):
    session = fields.IntegerField(attribute="session_id")

    class Meta:
        queryset = Event.objects.all()
        resource_name = "event"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()
        filtering = {
            "event_type": ('exact', 'startswith',),
            "server_time": ('exact', 'gte', 'lte', 'range'),
            "session": ('exact'),
        }


class SessionResource(ModelResource):
    project = fields.IntegerField(attribute="project_id")
    language = fields.IntegerField(attribute="language_id")

    class Meta:
        queryset = Session.objects.all()
        resource_name = "session"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()
        filtering = {
            "client_type": ('exact', 'contains',),
            "client_system": ('exact', 'contains'),
            "starttime": ('exact', 'gte', 'lte', 'range'),
            "demo_stream_enabled": ('exact'),
            "project": ('exact'),
            "language": ('exact'),
        }


class ListeningHistoryItemResource(ModelResource):
    session = fields.IntegerField(attribute="session_id")
    asset = fields.IntegerField(attribute="asset_id")
    duration_in_seconds = fields.FloatField(attribute="duration_in_seconds")

    class Meta:
        queryset = ListeningHistoryItem.objects.all()
        resource_name = "history"
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()
        filtering = {
            "duration": ('lte', 'gte'),
            "server_time": ('exact', 'gte', 'lte', 'range'),
            "session": ('exact'),
            "asset": ('exact'),
        }
