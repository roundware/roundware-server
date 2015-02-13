# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework object serializers for the V2 API.
from __future__ import unicode_literals
from roundware.rw.models import Asset, Event, ListeningHistoryItem, Project, Tag, Session
from roundware.lib.api import get_project_tags
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class AssetSerializer(serializers.ModelSerializer):
    audiolength_in_seconds = serializers.FloatField()

    class Meta:
        model = Asset


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


class ProjectSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Project

    def get_tags(self, project):
        return get_project_tags(p=project, s=None)


class ListenEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningHistoryItem


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session


class StreamSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    project_id = serializers.IntegerField(required=False)
    tags = serializers.CharField(max_length=255, required=False)

    lat = serializers.FloatField(required=False)
    long = serializers.FloatField(required=False)
    url = serializers.URLField(required=False)

    def validate_session_id(self, attrs, source):
        """
        Check the required session_id field.
        """
        session_id = attrs[source]
        if not Session.objects.filter(pk=session_id).exists():
            raise ValidationError("session_id=%s does not exist." % session_id)

        return attrs

    def validate(self, attrs):
        """
        Validate additional Stream data.
        """

        session = Session.objects.get(pk=attrs['session_id'])
        project = session.project

        if 'project_id' in attrs and attrs['project_id'] != project.id:
            raise ValidationError("project_id=%s does not match session.project=%s." %
                                  (attrs['project_id'], project.id))
        # Set project_id to make sure it exists.
        attrs['project_id'] = project.id

        # TODO: Validate tags against available project tags
        # if 'tags' in attrs:
        return attrs


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=False)
    device_id = serializers.CharField(max_length=255, required=False)
    client_type = serializers.CharField(max_length=255, required=False)

    def validate(self, attrs):
        """
        Validates the data used to instantiate the serializer
        """
        if "device_id" in attrs and "client_type" in attrs:
            return attrs
        else:
            raise ValidationError("Invalid user request")

    def create(self, validated_data):
        """
        Creates a new user object for the serializer's .save() method
        """
        username = validated_data["device_id"][:29]
        password = User.objects.make_random_password()
        user = User.objects.create_user(username=username, password=password)
        user.userprofile.device_id = validated_data["device_id"][:254]
        user.userprofile.client_type = validated_data["client_type"][:254]
        user.userprofile.save()
        return user
