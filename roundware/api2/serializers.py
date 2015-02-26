# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework object serializers for the V2 API.
from __future__ import unicode_literals
from roundware.rw.models import Asset, Event, Language, ListeningHistoryItem, Project, Tag, Session, LocalizedString
from roundware.lib.api import request_stream
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth.models import User
import time
import logging

logger = logging.getLogger(__name__)


# class AssetSerializer(serializers.ModelSerializer):
#     audiolength_in_seconds = serializers.FloatField()

#     class Meta:
#         model = Asset


# class EventSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Event


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project

    def to_representation(self, obj):
        result = super(ProjectSerializer, self).to_representation(obj)
        if 'session' in self.context:
            for key in result.keys():
                if key[-4:] == "_loc" and type(result[key]) is list:
                    msg = None
                    default = None
                    for loc_item in result[key]:
                        loc_string = LocalizedString.objects.get(pk=loc_item)
                        if loc_string.language == self.context["session"].language:
                            msg = loc_string.localized_string
                        if loc_string.language.language_code == "en":
                            default = loc_string.localized_string
                    result[key[:-4]] = msg or default
                    del result[key]
        return result

# class ListenEventSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ListeningHistoryItem


class SessionSerializer(serializers.ModelSerializer):
    starttime = serializers.DateTimeField(required=True)
    language = serializers.CharField(max_length=2, default="en")
    client_system = serializers.CharField(max_length=128, required=True)

    class Meta:
        model = Session

    def validate_language(self, value):
        try:
            Language.objects.get(language_code=value)
        except Language.DoesNotExist:
            raise ValidationError("Language Code %s not found" % value)
        return value

    def create(self, validated_data):
        lang = Language.objects.get(language_code=validated_data['language'])
        session = Session.objects.create(device_id=self.context["request"].user.userprofile.device_id,
                                         project=validated_data["project"],
                                         starttime=validated_data["starttime"],
                                         language_id=lang.pk,
                                         client_type=self.context["request"].user.userprofile.client_type,
                                         client_system=validated_data["client_system"])
        session.save()
        return session


class StreamSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    project_id = serializers.IntegerField(required=False)
    tags = serializers.CharField(max_length=255, required=False)

    lat = serializers.FloatField(required=False)
    long = serializers.FloatField(required=False)
    url = serializers.URLField(required=False)

    def validate_session_id(self, value):
        """
        Check the required session_id field.
        """
        if not Session.objects.filter(pk=value).exists():
            raise ValidationError("session_id=%s does not exist." % value)

        return value

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

    def create(self, vdata):
        stream = request_stream(self.context['request'])
        stream['stream_id'] = vdata['session_id']
        return stream


# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag


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
        username = str(int(time.time())) + validated_data["device_id"][-4:]
        password = User.objects.make_random_password()
        user = User.objects.create_user(username=username, password=password)
        user.userprofile.device_id = validated_data["device_id"][:254]
        user.userprofile.client_type = validated_data["client_type"][:254]
        user.userprofile.save()
        return user
