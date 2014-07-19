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


class AssetList(generics.ListAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

class AssetLocationList(generics.ListAPIView):
    queryset = Asset.objects.filter()
    serializer_class = AssetLocationSerializer
    fields = ['latitude', 'longitude', 'id', 'filename', 'description']


class ProjectList(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class EventList(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer



class SessionList(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class ListeningHistoryItemList(generics.ListAPIView):
    queryset = ListeningHistoryItem.objects.all()
    serializer_class = ListeningHistoryItemAssetSerializer
