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
from roundware.rw.serializers_api1 import (AssetSerializer,
                                           AssetLocationSerializer,
                                           ProjectSerializer,
                                           EventSerializer,
                                           SessionSerializer,
                                           ListeningHistoryItemAssetSerializer)
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions
import django_filters

class APIRootView(APIView):
    def get(self, request, format=None):
        data = {
            'assets': reverse('api1-asset', request=request, format=format),
            'assetlocations': reverse('api1-assetlocation', request=request, format=format),
            'projects': reverse('api1-project', request=request, format=format),
            'events': reverse('api1-event', request=request, format=format),
            'sessions': reverse('api1-session', request=request, format=format),
            'listeninghistoryitems': reverse('api1-listeninghistoryitem', request=request, format=format),

        }
        return Response(data)


class AssetFilter(django_filters.FilterSet):
    mediatype__contains = django_filters.CharFilter(name='mediatype', lookup_type='startswith')

    created__gte = django_filters.DateTimeFilter(name='created', lookup_type='gte')
    created__lte = django_filters.DateTimeFilter(name='created', lookup_type='lte')
    created__range = django_filters.DateRangeFilter(name='created')
    audiolength__lte = django_filters.NumberFilter('audiolength', lookup_type='lte')
    audiolength__gte = django_filters.NumberFilter('audiolength', lookup_type='gte')

    class Meta:
        model = Asset
        fields = ['mediatype',
                  'submitted',
                  'created',
                  'project',
                  'language',
                  'session',
                  ]


class AssetList(generics.ListAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filter_class = AssetFilter


class AssetLocationList(generics.ListAPIView):
    queryset = Asset.objects.filter()
    serializer_class = AssetLocationSerializer
    # Only authenticated users can access this view
    permission_classes = (permissions.IsAuthenticated,)
    filter_class = AssetFilter


class AssetLocationDetail(generics.RetrieveUpdateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetLocationSerializer
    # Only authenticated users can access this view
    permission_classes = (permissions.IsAuthenticated,)


class ProjectList(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class EventFilter(django_filters.FilterSet):
    event_type__startswith = django_filters.CharFilter(name='event_type', lookup_type='startswith')
    server_time__gte = django_filters.DateTimeFilter(name='server_time', lookup_type='gte')
    server_time__lte = django_filters.DateTimeFilter(name='server_time', lookup_type='lte')
    server_time__range = django_filters.DateRangeFilter(name='server_time')
    class Meta:
        model = Event
        fields = ['event_type',
                  'server_time',
                  'session',
                  ]


class EventList(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_class = EventFilter


class SessionFilter(django_filters.FilterSet):
    client_type__contains = django_filters.CharFilter(name='client_type', lookup_type='contains')
    client_system__contains = django_filters.CharFilter(name='client_system', lookup_type='contains')

    starttime__gte = django_filters.DateTimeFilter(name='starttime', lookup_type='gte')
    starttime__lte = django_filters.DateTimeFilter(name='starttime', lookup_type='lte')
    starttime__range = django_filters.DateRangeFilter(name='starttime')
    class Meta:
        model = Session
        fields = ['client_type',
                  'client_system',
                  'starttime',
                  'demo_stream_enabled',
                  'project',
                  'language',
                  ]


class SessionList(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filter_class = SessionFilter


class ListeningHistoryItemFilter(django_filters.FilterSet):
    duration__lte = django_filters.NumberFilter('duration', lookup_type='lte')
    duration__gte = django_filters.NumberFilter('duration', lookup_type='gte')

    starttime__gte = django_filters.DateTimeFilter(name='starttime', lookup_type='gte')
    starttime__lte = django_filters.DateTimeFilter(name='starttime', lookup_type='lte')
    starttime__range = django_filters.DateRangeFilter(name='starttime')
    class Meta:
        model = ListeningHistoryItem
        fields = ['starttime',
                  'session',
                  'asset',
                  ]


class ListeningHistoryItemList(generics.ListAPIView):
    queryset = ListeningHistoryItem.objects.all()
    serializer_class = ListeningHistoryItemAssetSerializer
    filter_class = ListeningHistoryItemFilter
