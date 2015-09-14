# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework object serializers for the V2 API.
from __future__ import unicode_literals
from roundware.rw.models import (Asset, Event, Envelope, Language, ListeningHistoryItem,
                                 Project, Tag, Session, LocalizedString, Vote)
from roundware.lib.api import request_stream, vote_count_by_asset
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth.models import User
from datetime import datetime
import time
import re
import logging

logger = logging.getLogger(__name__)


class AssetSerializer(serializers.ModelSerializer):
    audiolength_in_seconds = serializers.FloatField(required=False)
    description = serializers.CharField(max_length=2048, default="")

    class Meta:
        model = Asset

    def to_representation(self, obj):
        result = super(AssetSerializer, self).to_representation(obj)
        # consistent naming for output
        result["asset_id"] = result["id"]
        del result["id"]

        result["media_type"] = result["mediatype"]
        del result["mediatype"]

        result["audio_length_in_seconds"] = result["audiolength_in_seconds"]
        del result["audiolength_in_seconds"]
        del result["audiolength"]

        result["tag_ids"] = result["tags"]
        del result["tags"]

        result["session_id"] = result["session"]
        del result["session"]

        del result["initialenvelope"]
        # load string version of language
        if "language" in result and result["language"] is not None:
            lang = Language.objects.get(pk=result["language"])
            result["language"] = lang.language_code

        return result


class EnvelopeSerializer(serializers.ModelSerializer):
    session_id = serializers.IntegerField(required=True)
    session = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Envelope

    def validate_session_id(self, value):
        try:
            self.context["session"] = Session.objects.get(pk=value)
        except Session.DoesNotExist:
            raise ValidationError("Session not found")
        return value

    def create(self, data):
        envelope = Envelope.objects.create(session=self.context["session"])
        envelope.save()
        return envelope

    def to_representation(self, obj):
        result = super(EnvelopeSerializer, self).to_representation(obj)
        result["envelope_id"] = result["id"]
        del result["id"]
        del result["session"]
        return result


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event

    def to_representation(self, obj):
        result = super(EventSerializer, self).to_representation(obj)
        result["event_id"] = result["id"]
        del result["id"]
        result["session_id"] = result["session"]
        del result["session"]
        result["tag_ids"] = result["tags"]
        del result["tags"]
        return result


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project

    def to_representation(self, obj):
        # must include only the related localizationStrings that match out session language
        result = super(ProjectSerializer, self).to_representation(obj)
        # session should be passed in as context
        session = None
        if 'session' in self.context:
            session = self.context["session"]
        # find the localizedString relation fields
        for key in result.keys():
            if key[-4:] == "_loc" and type(result[key]) is list:
                result[key[:-4]] = _select_localized_string(result[key], session)
                del result[key]
        result["project_id"] = result["id"]
        del result["id"]
        return result


class ListenEventSerializer(serializers.ModelSerializer):
    duration_in_seconds = serializers.FloatField(required=False)

    class Meta:
        model = ListeningHistoryItem

    def to_representation(self, obj):
        result = super(ListenEventSerializer, self).to_representation(obj)
        result["listenevent_id"] = result["id"]
        del result["id"]
        result["start_time"] = result["starttime"]
        del result["starttime"]
        result["session_id"] = result["session"]
        del result["session"]
        result["asset_id"] = result["asset"]
        del result["asset"]
        del result["duration"]
        return result


class SessionSerializer(serializers.Serializer):
    timezone = serializers.CharField(default="0000")
    language = serializers.CharField(max_length=2, default="en")
    client_system = serializers.CharField(max_length=128, required=True)
    project_id = serializers.IntegerField(required=True)

    def validate_language(self, value):
        try:
            Language.objects.get(language_code=value)
        except Language.DoesNotExist:
            # raise ValidationError("Language Code %s not found" % value)
            value = "en"
        return value

    def validate_timezone(self, value):
        if re.match("^[+-]?\d{4}$", value) is None:
            raise ValidationError("Timezone must be in RFC822 GMT format (e.g. '-0800')")
        return value

    def create(self, validated_data):
        lang = Language.objects.get(language_code=validated_data['language'])
        session = Session.objects.create(device_id=self.context["request"].user.userprofile.device_id,
                                         project_id=validated_data["project_id"],
                                         starttime=datetime.utcnow(),
                                         timezone=validated_data["timezone"],
                                         language_id=lang.pk,
                                         client_type=self.context["request"].user.userprofile.client_type,
                                         client_system=validated_data["client_system"])
        session.save()
        self.context["session_id"] = session.pk
        return session

    def to_representation(self, obj):
        result = super(SessionSerializer, self).to_representation(obj)
        result.update({"language": self.validated_data["language"]})
        if "session_id" in self.context:
            result["session_id"] = self.context["session_id"]
        return result


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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag

    def to_representation(self, obj):
        result = super(TagSerializer, self).to_representation(obj)
        # find correct localized strings
        session = None
        if "session" in self.context:
            session = self.context["session"]
        for field in ["loc_msg", "loc_description"]:
            result[field] = _select_localized_string(result[field], session=session)
        # field renaming
        result["tag_id"] = result["id"]
        del result["id"]
        return result


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


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote

    def to_representation(self, obj):
        result = super(VoteSerializer, self).to_representation(obj)
        result["vote_id"] = result["id"]
        del result["id"]
        result["asset_id"] = result["asset"]
        del result["asset"]
        result["session_id"] = result["session"]
        del result["session"]
        result["asset_votes"] = vote_count_by_asset(result["asset_id"])
        return result


def _select_localized_string(loc_str_ids, session=None):
    if session is not None:
        # find matching language
        try:
            lang = Language.objects.get(language_code=session.language)
        except Language.DoesNotExist:
            lang = Language.objects.get(language_code="en")
    else:
        lang = Language.objects.get(language_code="en")
    for loc_str_id in loc_str_ids:
        loc_str = LocalizedString.objects.get(pk=loc_str_id)
        if loc_str.language == lang:
            return loc_str.localized_string
    return None
