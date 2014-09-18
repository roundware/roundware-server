# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework object serializers for the V2 API.
from __future__ import unicode_literals
from roundware.rw.models import (Asset, Event, ListeningHistoryItem, Project,
                                 Session, Tag)
from rest_framework import serializers

class Asset(serializers.ModelSerializer):
    audiolength_in_seconds = serializers.FloatField()
    class Meta:
        model = Asset

class Event(serializers.ModelSerializer):
    class Meta:
        model = Event

class Project(serializers.ModelSerializer):
    class Meta:
        model = Project

class ListenEvent(serializers.ModelSerializer):
    class Meta:
        model = ListeningHistoryItem

class Session(serializers.ModelSerializer):
    class Meta:
        model = Session

class Tag(serializers.ModelSerializer):
    class Meta:
        model = Tag
