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
            'listeninghistory': reverse('api1-listeninghistory', request=request, format=format),

        }
        return Response(data)

class AssetList(generics.ListAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class AssetLocationList(generics.ListAPIView):
    queryset = Asset.objects.filter()
    serializer_class = AssetLocationSerializer
    # Only authenticated users can access this view
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('project', 'latitude')


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


class SessionList(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class ListeningHistoryItemList(generics.ListAPIView):
    queryset = ListeningHistoryItem.objects.all()
    serializer_class = ListeningHistoryItemAssetSerializer
