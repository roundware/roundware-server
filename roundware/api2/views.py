# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework Views for the V2 API.
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings
from roundware.rw.models import (Asset, Audiotrack, Event, Envelope, Language, ListeningHistoryItem,
                                 LocalizedString, Project, ProjectGroup, Session, Speaker, Tag, TagCategory,
                                 TagRelationship, TimedAsset, UIElement, UIElementName, UIGroup,
                                 UIItem, UserProfile, Vote)
from roundware.api2 import serializers
from roundware.api2.filters import (AssetFilterSet, AudiotrackFilterSet, EnvelopeFilterSet, EventFilterSet,
                                    LanguageFilterSet, ListeningHistoryItemFilterSet, LocalizedStringFilterSet,
                                    ProjectFilterSet, ProjectGroupFilterSet, SessionFilterSet, SpeakerFilterSet,
                                    TagFilterSet, TagCategoryFilterSet, TagRelationshipFilterSet, TimedAssetFilterSet,
                                    UIConfigFilterSet, UIElementFilterSet, UIElementNameFilterSet,
                                    UIGroupFilterSet, UIItemFilterSet, VoteFilterSet)
from roundware.lib.api import (get_project_tags_new as get_project_tags, modify_stream, move_listener, heartbeat,
                               skip_ahead, pause, resume, add_asset_to_envelope, get_currently_streaming_asset,
                               save_asset_from_request, vote_asset, check_is_active, get_projects_by_location,
                               vote_count_by_asset, log_event, play, kill)
from roundware.api2.permissions import AuthenticatedReadAdminWrite
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.authtoken.models import Token
from rest_framework.decorators import detail_route, list_route
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, DjangoFilterBackend
import logging
from random import sample
from datetime import datetime
from distutils.util import strtobool
from collections import OrderedDict
try:
    from profiling import profile
except ImportError: # pragma: no cover
    pass

logger = logging.getLogger(__name__)


# Note: Keep this stuff in alphabetical order!

class AssetPaginationMixin(object):

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination
        is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(
            queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given
        output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class AssetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 10000


class AssetViewSet(viewsets.GenericViewSet, AssetPaginationMixin,):
    """
    API V2: api/2/assets/
            api/2/assets/:id/
            api/2/assets/:id/votes/
            api/2/assets/random/
    """

    # TODO: Implement DjangoObjectPermissions
    queryset = Asset.objects.prefetch_related('tags', 'loc_description', 'loc_alt_text', 'envelope') \
                            .select_related('session', 'project', 'language', 'initialenvelope').all()
    permission_classes = (IsAuthenticated,)
    pagination_class = AssetPagination
    serializer_class = serializers.AssetSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    ordering_fields = ('id', 'session_id', 'audiolength', 'weight', 'volume')
    filter_class = AssetFilterSet

    # @profile(stats=True)
    def list(self, request):
        """
        GET api/2/assets/ - retrieve list of Assets filtered by parameters
        """
        assets = self.filter_queryset(self.get_queryset())
        if "paginate" in request.query_params:
            paginate = strtobool(request.query_params['paginate'])
        else:
            paginate = False

        page = self.paginate_queryset(assets)
        if page is not None and paginate:
            serializer = self.get_serializer(page, context={"admin": "admin" in request.query_params}, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(assets, context={"admin": "admin" in request.query_params}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/assets/:id/ - Get Asset by id
        """
        try:
            asset = Asset.objects.get(pk=pk)
        except Asset.DoesNotExist:
            raise Http404("Asset not found")
        serializer = serializers.AssetSerializer(asset, context={"admin": "admin" in request.query_params})
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/assets/ - Create a new Asset
        """
        if "file" not in request.data:
            raise ParseError("Must supply file for asset content")
        if not request.data["envelope_ids"].isdigit():
            raise ParseError("Must provide a single envelope_id in envelope_ids parameter for POST. "
                             "You can add more envelope_ids in subsequent PATCH calls")
        try:
            result = add_asset_to_envelope(request, envelope_id=request.data["envelope_ids"])
        except Exception as e:
            return Response({"detail": str(e)}, status.HTTP_400_BAD_REQUEST)
        asset_obj = Asset.objects.get(pk=result['asset_id'])
        serializer = serializers.AssetSerializer(asset_obj)
        return Response(serializer.data)

    def partial_update(self, request, pk):
        """
        PATCH api/2/assets/:id/ - Update existing Asset
        """
        try:
            asset = Asset.objects.get(pk=pk)
        except Asset.DoesNotExist:
            raise Http404("Asset not found")
        if 'tag_ids' in request.data:
            request.data['tags'] = request.data['tag_ids']
            del request.data['tag_ids']
        if 'language_id' in request.data:
            request.data['language'] = request.data['language_id']
            del request.data['language_id']
        if 'project_id' in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        if 'description_loc_ids' in request.data:
            request.data['loc_description'] = request.data['description_loc_ids']
            del request.data['description_loc_ids']
        if 'alt_text_loc_ids' in request.data:
            request.data['loc_alt_text'] = request.data['alt_text_loc_ids']
            del request.data['alt_text_loc_ids']
        if 'envelope_ids' in request.data:
            request.data['envelope_set'] = request.data['envelope_ids']
            del request.data['envelope_ids']
        serializer = serializers.AssetSerializer(asset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/assets/:id/ - Delete an Asset
        """
        try:
            asset = Asset.objects.get(pk=pk)
        except Asset.DoesNotExist:
            raise Http404("Asset not found; cannot delete!")
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post', 'get'])
    def votes(self, request, pk=None):
        """
        GET api/2/assets/votes/ - retrieve Votes for specified Asset
        POST api/2/assets/votes/ - create Vote for specified Asset
        """
        if request.method == "POST":
            vote_op = vote_asset(request, asset_id=pk)
            vote = vote_op["vote"]
            serializer = serializers.VoteSerializer(vote)
            return Response(serializer.data)
        else:
            count = vote_count_by_asset(pk)
            return Response(count)

    @list_route(methods=['get'])
    def random(self, request, pk=None):
        """
        GET api/2/assets/random/ - retrieve random list of Assets filtered by parameters
        """
        assets = AssetFilterSet(request.query_params).qs.values_list('id', flat=True)
        asset_count = len(assets)
        if asset_count is 0:
            return Response([])
        # ensure limit isn't greater than asset_count which causes sample to fail
        limit = min(int(request.query_params.get('limit', 1)), asset_count)
        # ensure indices returned are unique
        random_idx = sample(range(asset_count), limit)
        selected_ids = [assets[x] for x in random_idx]
        results = Asset.objects.filter(id__in=selected_ids)
        serializer = serializers.AssetSerializer(results, many=True)
        return Response(serializer.data)


class AudiotrackViewSet(viewsets.ViewSet):
    """
    API V2: api/2/audiotracks/
            api/2/audiotracks/:id/
    """
    queryset = Audiotrack.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return Audiotrack.objects.get(pk=pk)
        except Audiotrack.DoesNotExist:
            raise Http404("Audiotrack not found")

    def list(self, request):
        """
        GET api/2/audiotracks/ - Provides list of Audiotracks filtered by parameters
        """
        audiotracks = AudiotrackFilterSet(request.query_params)
        serializer = serializers.AudiotrackSerializer(audiotracks, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/audiotracks/:id/ - Get Audiotrack by id
        """
        audiotrack = self.get_object(pk)
        # session_id not needed, because no localization..?
        serializer = serializers.AudiotrackSerializer(audiotrack)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/audiotracks/ - Create a new Audiotrack
        """
        if "project_id" in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        # convert from seconds to nanoseconds
        if 'minduration' in request.data:
            request.data['minduration'] = float(request.data['minduration']) * float(1000000000)
        if 'maxduration' in request.data:
            request.data['maxduration'] = float(request.data['maxduration']) * float(1000000000)
        if 'mindeadair' in request.data:
            request.data['mindeadair'] = float(request.data['mindeadair']) * float(1000000000)
        if 'maxdeadair' in request.data:
            request.data['maxdeadair'] = float(request.data['maxdeadair']) * float(1000000000)
        if 'minfadeintime' in request.data:
            request.data['minfadeintime'] = float(request.data['minfadeintime']) * float(1000000000)
        if 'maxfadeintime' in request.data:
            request.data['maxfadeintime'] = float(request.data['maxfadeintime']) * float(1000000000)
        if 'minfadeouttime' in request.data:
            request.data['minfadeouttime'] = float(request.data['minfadeouttime']) * float(1000000000)
        if 'maxfadeouttime' in request.data:
            request.data['maxfadeouttime'] = float(request.data['maxfadeouttime']) * float(1000000000)
        if 'minpanduration' in request.data:
            request.data['minpanduration'] = float(request.data['minpanduration']) * float(1000000000)
        if 'maxpanduration' in request.data:
            request.data['maxpanduration'] = float(request.data['maxpanduration']) * float(1000000000)
        serializer = serializers.AudiotrackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/audiotracks/:id/ - Update existing Audiotrack
        """
        audiotrack = self.get_object(pk)
        if "project_id" in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        # convert from seconds to nanoseconds
        if 'minduration' in request.data:
            request.data['minduration'] = float(request.data['minduration']) * float(1000000000)
        if 'maxduration' in request.data:
            request.data['maxduration'] = float(request.data['maxduration']) * float(1000000000)
        if 'mindeadair' in request.data:
            request.data['mindeadair'] = float(request.data['mindeadair']) * float(1000000000)
        if 'maxdeadair' in request.data:
            request.data['maxdeadair'] = float(request.data['maxdeadair']) * float(1000000000)
        if 'minfadeintime' in request.data:
            request.data['minfadeintime'] = float(request.data['minfadeintime']) * float(1000000000)
        if 'maxfadeintime' in request.data:
            request.data['maxfadeintime'] = float(request.data['maxfadeintime']) * float(1000000000)
        if 'minfadeouttime' in request.data:
            request.data['minfadeouttime'] = float(request.data['minfadeouttime']) * float(1000000000)
        if 'maxfadeouttime' in request.data:
            request.data['maxfadeouttime'] = float(request.data['maxfadeouttime']) * float(1000000000)
        if 'minpanduration' in request.data:
            request.data['minpanduration'] = float(request.data['minpanduration']) * float(1000000000)
        if 'maxpanduration' in request.data:
            request.data['maxpanduration'] = float(request.data['maxpanduration']) * float(1000000000)
        serializer = serializers.AudiotrackSerializer(audiotrack, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/audiotracks/:id/ - Delete Audiotrack
        """
        audiotrack = self.get_object(pk)
        audiotrack.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnvelopeViewSet(viewsets.ViewSet):
    """
    API V2: api/2/envelopes/
            api/2/envelopes/:id/
    """
    queryset = Envelope.objects.all()

    def list(self, request):
        """
        GET api/2/envelopes/ - retrieve list of Envelopes
        """
        envelopes = EnvelopeFilterSet(request.query_params)
        serializer = serializers.EnvelopeSerializer(envelopes, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/envelopes/:id/ - Get Envelope by id
        """
        try:
            envelope = Envelope.objects.get(pk=pk)
        except Envelope.DoesNotExist:
            raise Http404("Envelope not found")
        serializer = serializers.EnvelopeSerializer(envelope)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/envelopes/ - Creates a new Envelope based on passed session_id
        """
        serializer = serializers.EnvelopeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """
        PATCH api/2/envelopes/:id/ - Adds an Asset to the Envelope
        """
        if "asset_id" in request.data or "file" in request.FILES:
            try:
                result = add_asset_to_envelope(request, envelope_id=pk)
            except Exception as e:
                return Response({"detail": str(e)}, status.HTTP_400_BAD_REQUEST)
            asset_obj = Asset.objects.get(pk=result['asset_id'])
            serializer = serializers.AssetSerializer(asset_obj)
            return Response(serializer.data)
        else:
            raise ParseError("asset_id or file required")


class EventViewSet(viewsets.ViewSet):
    """
    API V2: api/2/events/
            api/2/events/:id/
    """

    # TODO: Implement ViewCreate permission.
    queryset = Event.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        GET api/2/events/ - Provides list of Events filtered by parameters
        """
        events = EventFilterSet(request.query_params)
        serializer = serializers.EventSerializer(events, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/events/:id/ - Get Event by id
        """
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404("Event not found")
        serializer = serializers.EventSerializer(event)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/events/ - Create a new Event
        """
        if 'session_id' not in request.data:
            raise ParseError("a session_id is required for this operation")
        if 'event_type' not in request.data:
            raise ParseError("an event_type is required for this operation")
        try:
            e = log_event(request.data['event_type'], request.data['session_id'], request.data)
        except Exception as e:
            raise ParseError(str(e))
        serializer = serializers.EventSerializer(e)
        return Response(serializer.data)


class LanguageViewSet(viewsets.ViewSet):
    """
    API V2: api/2/languages/
            api/2/languages/:id/
    """
    queryset = Language.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return Language.objects.get(pk=pk)
        except Language.DoesNotExist:
            raise Http404("Language not found")

    def list(self, request):
        """
        GET api/2/Languages/ - Provides list of Languages filtered by parameters
        """
        languages = LanguageFilterSet(request.query_params)
        serializer = serializers.LanguageSerializer(languages, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/languages/:id/ - Get Language by id
        """
        language = self.get_object(pk)
        serializer = serializers.LanguageSerializer(language)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/languages/ - Create a new Language
        """
        serializer = serializers.LanguageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/languages/:id/ - Update existing Language
        """
        language = self.get_object(pk)
        serializer = serializers.LanguageSerializer(language, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/languages/:id/ - Delete a Language
        """
        language = self.get_object(pk)
        language.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListenEventViewSet(viewsets.ViewSet):
    """
    API V2: api/2/listenevents/
            api/2/listenevents/:id/
    """

    # TODO: Rename ListeningHistoryItem model to ListenEvent.
    queryset = ListeningHistoryItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        GET api/2/listenevents/ - Get ListenEvents by filtering parameters
        """
        events = ListeningHistoryItemFilterSet(request.query_params)
        serializer = serializers.ListenEventSerializer(events, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/listenevents/:id/ - Get ListenEvent by id
        """
        try:
            event = ListeningHistoryItem.objects.get(pk=pk)
        except ListeningHistoryItem.DoesNotExist:
            raise Http404("ListenEvent not found")
        serializer = serializers.ListenEventSerializer(event)
        return Response(serializer.data)


class LocalizedStringViewSet(viewsets.ViewSet):
    """
    API V2: api/2/localizedstrings/
            api/2/localizedstrings/:id/
    """
    queryset = LocalizedString.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return LocalizedString.objects.get(pk=pk)
        except LocalizedString.DoesNotExist:
            raise Http404("LocalizedString not found")

    def list(self, request):
        """
        GET api/2/localizedstrings/ - Provides list of LocalizedStrings filtered by parameters
        """
        localizedstrings = LocalizedStringFilterSet(request.query_params)
        serializer = serializers.LocalizedStringSerializer(localizedstrings, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/localizedstrings/:id/ - Get LocalizedString by id
        """
        localizedstring = self.get_object(pk)
        serializer = serializers.LocalizedStringSerializer(localizedstring)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/localizedstrings/ - Create a new LocalizedString
        """
        if 'language_id' in request.data:
            request.data['language'] = request.data['language_id']
            del request.data['language_id']
        if 'text' in request.data:
            request.data['localized_string'] = request.data['text']
            del request.data['text']
        serializer = serializers.LocalizedStringSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/localizedstrings/:id/ - Update existing LocalizedString
        """
        localizedstring = self.get_object(pk)
        if 'language_id' in request.data:
            request.data['language'] = request.data['language_id']
            del request.data['language_id']
        if 'text' in request.data:
            request.data['localized_string'] = request.data['text']
            del request.data['text']
        serializer = serializers.LocalizedStringSerializer(localizedstring, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/localizedstrings/:id/ - Delete a LocalizedString
        """
        localizedstring = self.get_object(pk)
        localizedstring.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectViewSet(viewsets.ViewSet):
    """
    API V2: api/2/projects/
            api/2/projects/:id/
            api/2/projects/:id/tags/
            api/2/projects/:id/uigroups/
            api/2/projects/:id/uiconfig/
            api/2/projects/:id/assets/
            api/2/projects/:id/uielements/
    """
    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404("Project not found")

    def list(self, request):
        """
        GET api/2/projects/ - Provides list of Projects filtered by parameters
        """
        projects = ProjectFilterSet(request.query_params)
        serializer = serializers.ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/projects/:id/ - Get Project by id
        """
        if "session_id" in request.query_params:
            session = get_object_or_404(Session, pk=request.query_params["session_id"])
            project = get_object_or_404(Project, pk=pk)
            serializer = serializers.ProjectSerializer(project,
                                                       context={"session": session,
                                                                "admin": "admin" in request.query_params})
        else:
            raise ParseError("session_id parameter is required")
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/projects/ - Create a new Project
        """
        if 'language_ids' in request.data:
            request.data['languages'] = request.data['language_ids']
            del request.data['language_ids']
        serializer = serializers.ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/projects/:id/ - Update existing Project
        """
        project = self.get_object(pk)
        if 'language_ids' in request.data:
            request.data['languages'] = request.data['language_ids']
            del request.data['language_ids']
        serializer = serializers.ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/projects/:id/ - Delete a Project
        """
        project = self.get_object(pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        """
        GET api/2/projects/:id/tags/ - Get Tags for specific Project
        """
        session = None
        if "session_id" in request.query_params:
            session = get_object_or_404(Session, pk=request.query_params["session_id"])

        tags = get_project_tags(p=pk)
        serializer = serializers.TagSerializer(tags, context={"session": session,
                                                              "admin": "admin" in request.query_params}, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def uigroups(self, request, pk=None):
        """
        GET api/2/projects/:id/uigroups/ - Get UIGroups for specific Project
        """
        params = request.query_params.copy()
        if "session_id" in params:
            try:
                session = Session.objects.get(pk=params["session_id"])
            except:
                raise ParseError("Session not found")
        params["project_id"] = pk
        uigroups = UIGroupFilterSet(params)
        serializer = serializers.UIGroupSerializer(uigroups,
                                                   context={"admin": "admin" in request.query_params,
                                                            "session": session}, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def uiconfig(self, request, pk=None):
        """
        GET api/2/projects/:id/uiconfig/ - Get UI config data for specific Project
        """
        params = request.query_params.copy()
        if "session_id" in params:
            try:
                session = Session.objects.get(pk=params["session_id"])
            except:
                raise ParseError("Session not found")
        params["project_id"] = pk
        params['active'] = 'true'
        params['ui_mode'] = 'listen'
        uigroups_listen = UIGroupFilterSet(params)
        serializer_listen = serializers.UIConfigSerializer(uigroups_listen,
                                                   context={"admin": "admin" in request.query_params,
                                                            "session": session, "mode": "listen"}, many=True)
        sld = serializer_listen.data
        params['ui_mode'] = 'speak'
        uigroups_speak = UIGroupFilterSet(params)
        serializer_speak = serializers.UIConfigSerializer(uigroups_speak,
                                                   context={"admin": "admin" in request.query_params,
                                                            "session": session, "mode": "speak"}, many=True)
        ssd = serializer_speak.data
        return Response({ "listen" : sld,
                          "speak"  : ssd })

    @detail_route(methods=['get'])
    def assets(self, request, pk=None):
        """
        GET api/2/projects/:id/assets/ - Get Assets for specific Project
        """
        params = request.query_params.copy()
        params["project_id"] = pk
        assets = AssetFilterSet(params)
        # serialize and return
        serializer = serializers.AssetSerializer(assets, context={"admin": "admin" in request.query_params}, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def uielements(self, request, pk=None):
        """
        GET api/2/projects/:id/uielements/ - Get UIElements for specific Project
        """
        params = request.query_params.copy()
        if "language_code" in params:
            try:
                lc = Language.objects.get(language_code=params["language_code"])
            except:
                raise ParseError("Language Code not found")
        else:
            lc = Language.objects.get(language_code="en")
        if "variant" not in params:
            raise ParseError("Variant param is required.")
        params["project_id"] = pk
        uielements = UIElementFilterSet(params)
        r = {}
        # build data structure for each view individually
        for uielementview in UIElementName.VIEWS:
            current_ids = []
            for uielement in uielements:
                if uielement.uielementname.view == str(uielementview[0]):
                    current_ids.append(uielement.id)
            currentview_uielements = UIElement.objects.filter(id__in=current_ids)
            serializer = serializers.UIElementProjectSerializer(currentview_uielements,
                                                                context={"lc": lc.language_code},
                                                                many=True)
            # convert from list of dictionaries to dictionary of nested dictionaries
            s = {}
            for element in serializer.data:
                for key, value in element.items():
                    s[key] = value
            r[str(uielementview[0])] = s

        # different graphic asset zip file for each variant for each project
        zip_url = settings.MEDIA_URL + "project" + pk + "-uielements" + params['variant'] + ".zip"
        # put config as first item for human readability
        result = OrderedDict()
        result['config'] = { "files_url": zip_url}
        result['uielements'] = r
        return Response(result)


class ProjectGroupViewSet(viewsets.ViewSet):
    """
    API V2: api/2/projectgroups/
            api/2/projectgroups/:id/
            api/2/projectgroups/:id/projects/
    """
    queryset = ProjectGroup.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return ProjectGroup.objects.get(pk=pk)
        except ProjectGroup.DoesNotExist:
            raise Http404("ProjectGroup not found")

    def list(self, request):
        """
        GET api/2/projectgroups/ - Provides list of ProjectGroups filtered by parameters
        """
        projectgroups = ProjectGroupFilterSet(request.query_params)
        logger.info('ProjectGroup = %s' % projectgroups)
        serializer = serializers.ProjectGroupSerializer(projectgroups, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/projectgroups/:id/ - Get ProjectGroup by id
        """
        projectgroup = self.get_object(pk)
        serializer = serializers.ProjectGroupSerializer(projectgroup)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/projectgroups/ - Create a new ProjectGroup
        """
        if "project_ids" in request.data:
            request.data['projects'] = request.data['project_ids']
            del request.data['project_ids']
        serializer = serializers.ProjectGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/projectgroups/:id/ - Update existing ProjectGroup
        """
        projectgroup = self.get_object(pk)
        if "project_ids" in request.data:
            request.data['projects'] = request.data['project_ids']
            del request.data['project_ids']
        serializer = serializers.ProjectGroupSerializer(projectgroup, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/projectgroups/:id/ - Delete a ProjectGroup
        """
        projectgroup = self.get_object(pk)
        projectgroup.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['get'])
    def projects(self, request, pk=None):
        """
        GET api/2/projectgroups/:id/projects/ - Get Projects for specific ProjectGroup.
        This is the initial call the transforming app will make to see what projects are available.
        """
        projectgroup = self.get_object(pk)
        # check if project group is active
        if not projectgroup.active:
            return Response({"detail": "Project Group inactive; please try another one."})
        # language_code is optional with "en" as default
        if "language_code" in request.query_params:
            lc = request.query_params["language_code"]
        else:
            lc = "en"
        # if lat or lon don't exist, throw error message
        if "latitude" in request.query_params and "longitude" in request.query_params:
            lat = request.query_params["latitude"]
            lon = request.query_params["longitude"]
        else:
            return Response({"detail": "Both latitude and longitude parameters are required."})
        # filter for Projects in specified ProjectGroup
        projects = Project.objects.filter(projectgroup__in=pk)
        # filter for Projects at specified location
        projects_geo_filter = get_projects_by_location(projects, lat, lon)
        serializer = serializers.ProjectChooserSerializer(projects_geo_filter,
                                                          context={"language_code": lc},
                                                          many=True)
        return Response(serializer.data)


class SessionViewSet(viewsets.ViewSet):
    """
    API V2: api/2/sessions/
    """
    queryset = Session.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Session.objects.get(pk=pk)
        except Session.DoesNotExist:
            raise Http404("Session not found")

    def list(self, request):
        """
        GET api/2/sessions/ - Provides list of Sessions filtered by parameters
        """
        sessions = SessionFilterSet(request.query_params)
        serializer = serializers.SessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/sessions/:id/ - Get Session by id
        """
        session = self.get_object(pk)
        serializer = serializers.SessionSerializer(session)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/sessions/ - Create a new Session
        """
        if "project_id" in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        # set language properly based on either language or language_id param
        # default to 1/"en" if none passed
        if "language" in request.data:
            l = request.data['language']
            # convert from long-form language code if necessary
            if '-' in l:
                l = l.split('-')[0]
            lang = Language.objects.get(language_code=l)
            request.data['language'] = lang.pk
        elif "language_id" in request.data:
            request.data['language'] = request.data['language_id']
        else:
            request.data['language'] = 1
        # dynamically set params not passed, but required in Session model, as needed
        request.data['starttime'] = str(datetime.utcnow())
        request.data['device_id'] = request.user.userprofile.device_id
        if "client_type" not in request.data:
            request.data['client_type'] = request.user.userprofile.client_type
        # check if geo_listen_enabled is passed in request.data and if not,
        # add it with value from project.geo_listen_enabled
        # make request.data mutable to allow POST params to be sent as application/json
        # rather than requiring multipart/form-data
        rdm = request.data.copy()
        if 'geo_listen_enabled' not in rdm:
            p = Project.objects.get(id=rdm['project'])
            rdm['geo_listen_enabled'] = p.geo_listen_enabled
            logger.info('geo_listen_enabled not passed! set to project value: %s' % rdm['geo_listen_enabled'])
        serializer = serializers.SessionSerializer(data=rdm, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpeakerViewSet(viewsets.ViewSet):
    """
    API V2: api/2/speakers/
            api/2/speakers/:id/
    """
    queryset = Speaker.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return Speaker.objects.get(pk=pk)
        except Speaker.DoesNotExist:
            raise Http404("Speaker not found")

    def list(self, request):
        """
        GET api/2/speakers/ - Provides list of Speakers filtered by parameters
        """
        speakers = SpeakerFilterSet(request.query_params)
        serializer = serializers.SpeakerSerializer(speakers, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/speakers/:id/ - Get Speaker by id
        """
        speaker = self.get_object(pk)
        serializer = serializers.SpeakerSerializer(speaker)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/speakers/ - Create a new Speaker
        """
        if "project_id" in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        serializer = serializers.SpeakerSerializer(data=request.data)
        if serializer.is_valid():
            s = serializer.save()
            # re-retrieve the Speaker data after build_attenuation_buffer_line has run
            speaker = self.get_object(s.id)
            serializer = serializers.SpeakerSerializer(speaker)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/speakers/:id/ - Update existing Speaker
        """
        speaker = self.get_object(pk)
        if "project_id" in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        serializer = serializers.SpeakerSerializer(speaker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # re-retrieve the Speaker data after build_attenuation_buffer_line has run
            speaker = self.get_object(pk)
            serializer = serializers.SpeakerSerializer(speaker)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/speakers/:id/ - Delete a Speaker
        """
        speaker = self.get_object(pk)
        speaker.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StreamViewSet(viewsets.ViewSet):
    """
    The primary communication channel for handling the Roundware audio stream.
    API V2: api/2/streams/
            api/2/streams/:id/heartbeat/
            api/2/streams/:id/playasset/
            api/2/streams/:id/replayasset/
            api/2/streams/:id/skipasset/
            api/2/streams/:id/pause/
            api/2/streams/:id/resume/
            api/2/streams/:id/isactive/
            api/2/streams/:id/kill/
    """
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        serializer = serializers.StreamSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            raise ParseError(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.save())

    def partial_update(self, request, pk=None):
        try:
            if "tag_ids" in request.data:
                success = modify_stream(request, context={"pk": pk})
            elif "longitude" in request.data and "latitude" in request.data:
                success = move_listener(request, context={"pk": pk})
            else:
                raise ParseError("must supply something to update")
            if success["success"]:
                return Response()
            else:
                return Response({"detail": success["error"]},
                                status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "could not update stream: %s" % e},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def heartbeat(self, request, pk=None):
        try:
            heartbeat(request, session_id=pk)
            return Response()
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def playasset(self, request, pk=None):
        try:
            return Response(play({
                'session_id': pk,
                'asset_id': request.POST.get('asset_id')
            }))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def replayasset(self, request, pk=None):
        try:
            result = get_currently_streaming_asset(request, session_id=pk)
            return Response(play({
                'session_id': pk,
                'asset_id': str(result.get('asset_id'))
            }))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def skipasset(self, request, pk=None):
        try:
            return Response(skip_ahead(request, session_id=pk))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def pause(self, request, pk=None):
        try:
            return Response(pause(request, session_id=pk))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def resume(self, request, pk=None):
        try:
            return Response(resume(request, session_id=pk))
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def isactive(self, request, pk=None):
        try:
            result = check_is_active(pk)
            stream_id = int(pk)
            return Response({
                'stream_id': stream_id,
                'active': result
            })
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def kill(self, request, pk=None):
        try:
            result = kill(pk, "mp3")
            stream_id = int(pk)
            return Response({
                'stream_id': stream_id,
                'success': result
            })
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ViewSet):
    """
    API V2: api/2/tags/
            api/2/tags/:id/
    """
    # TODO: Return messages and relationships in response
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            raise Http404("Tag not found")

    def list(self, request):
        """
        GET api/2/tags/ - Provides list of Tags filtered by parameters
        """
        tags = TagFilterSet(request.query_params)
        session = None
        if "session_id" in request.query_params:
            try:
                session = Session.objects.get(pk=request.query_params["session_id"])
            except:
                raise ParseError("Session not found")
        serializer = serializers.TagSerializer(tags, context={"admin": "admin" in request.query_params,
                                                              "session": session}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/tags/:id/ - Get Tag by id
        """
        tag = self.get_object(pk)
        session = None
        if "session_id" in request.query_params:
            try:
                session = Session.objects.get(pk=request.query_params["session_id"])
            except:
                raise ParseError("Session not found")
        serializer = serializers.TagSerializer(tag, context={"session": session,
                                                             "admin": "admin" in request.query_params})
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/tags/ - Create a new Tag
        """
        if 'tag_category_id' in request.data:
            request.data['tag_category'] = request.data['tag_category_id']
            del request.data['tag_category_id']
        if 'project_id' in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        if 'description_loc_ids' in request.data:
            request.data['loc_description'] = request.data['description_loc_ids']
            del request.data['description_loc_ids']
        if 'msg_loc_ids' in request.data:
            request.data['loc_msg'] = request.data['msg_loc_ids']
            del request.data['msg_loc_ids']
        serializer = serializers.TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/tags/:id/ - Update existing Tag
        """
        tag = self.get_object(pk)
        if 'tag_category_id' in request.data:
            request.data['tag_category'] = request.data['tag_category_id']
            del request.data['tag_category_id']
        if 'project_id' in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        if 'description_loc_ids' in request.data:
            request.data['loc_description'] = request.data['description_loc_ids']
            del request.data['description_loc_ids']
        if 'msg_loc_ids' in request.data:
            request.data['loc_msg'] = request.data['msg_loc_ids']
            del request.data['msg_loc_ids']
        serializer = serializers.TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        POST api/2/tags/:id/ - Delete Tag
        """
        tag = self.get_object(pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagCategoryViewSet(viewsets.ViewSet):
    """
    API V2: api/2/tagcategories/
            api/2/tagcategories/:id/
    """
    queryset = TagCategory.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return TagCategory.objects.get(pk=pk)
        except TagCategory.DoesNotExist:
            raise Http404("TagCategory not found")

    def list(self, request):
        """
        GET api/2/tagcategories/ - Provides list of TagCategories filtered by parameters
        """
        tagcategories = TagCategoryFilterSet(request.query_params)
        serializer = serializers.TagCategorySerializer(tagcategories, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/tagcategories/:id/ - Get TagCategory by id
        """
        tagcategory = self.get_object(pk)
        serializer = serializers.TagCategorySerializer(tagcategory)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/tagcategories/ - Create a new TagCategory
        """
        serializer = serializers.TagCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/tagcategories/:id/ - Update existing TagCategory
        """
        tagcategory = self.get_object(pk)
        serializer = serializers.TagCategorySerializer(tagcategory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/tagcategories/:id/ - Delete a TagCategory
        """
        tagcategory = self.get_object(pk)
        tagcategory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagRelationshipViewSet(viewsets.ViewSet):
    """
    API V2: api/2/tagrelationships/
            api/2/tagrelationships/:id/
    """
    queryset = TagRelationship.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return TagRelationship.objects.get(pk=pk)
        except TagRelationship.DoesNotExist:
            raise Http404("TagRelationship not found")

    def list(self, request):
        """
        GET api/2/tagrelationships/ - Provides list of TagRelationship filtered by parameters
        """
        tagrelationships = TagRelationshipFilterSet(request.query_params)
        serializer = serializers.TagRelationshipSerializer(tagrelationships, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/tagrelationships/:id/ - Get TagRelationship by id
        """
        tagrelationship = self.get_object(pk)
        # session_id not needed, because no localization..?
        serializer = serializers.TagRelationshipSerializer(tagrelationship)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/tagrelationships/ - Create a new TagRelationship
        """
        if 'tag_id' in request.data:
            request.data['tag'] = request.data['tag_id']
            del request.data['tag_id']
        if 'parent_id' in request.data:
            request.data['parent'] = request.data['parent_id']
            del request.data['parent_id']
        serializer = serializers.TagRelationshipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/tagrelationships/:id/ - Update existing TagRelationship
        """
        tagrelationship = self.get_object(pk)
        if 'tag_id' in request.data:
            request.data['tag'] = request.data['tag_id']
            del request.data['tag_id']
        if 'parent_id' in request.data:
            request.data['parent'] = request.data['parent_id']
            del request.data['parent_id']
        serializer = serializers.TagRelationshipSerializer(tagrelationship, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/tagrelationships/:id/ - Delete a TagRelationship
        """
        tagrelationship = self.get_object(pk)
        tagrelationship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TimedAssetViewSet(viewsets.ViewSet):
    """
    API V2: api/2/timedassets/
            api/2/timedassets/:id/
    """
    queryset = TimedAsset.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return TimedAsset.objects.get(pk=pk)
        except TimedAsset.DoesNotExist:
            raise Http404("TimedAsset not found")

    def list(self, request):
        """
        GET api/2/timedassets/ - Provides list of TimedAssets filtered by parameters
        """
        timedassets = TimedAssetFilterSet(request.query_params)
        serializer = serializers.TimedAssetSerializer(timedassets, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/timedassets/:id/ - Get TimedAsset by id
        """
        timedasset = self.get_object(pk)
        serializer = serializers.TimedAssetSerializer(timedasset)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/timedassets/ - Create a new TimedAsset
        """
        if 'asset_id' in request.data:
            request.data['asset'] = request.data['asset_id']
            del request.data['asset_id']
        if 'project_id' in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        serializer = serializers.TimedAssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/timedassets/:id/ - Update existing TimedAsset
        """
        timedasset = self.get_object(pk)
        if 'asset_id' in request.data:
            request.data['asset'] = request.data['asset_id']
            del request.data['asset_id']
        if 'project_id' in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        serializer = serializers.TimedAssetSerializer(timedasset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/timedassets/:id/ - Delete a TimedAsset
        """
        timedasset = self.get_object(pk)
        timedasset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UIElementViewSet(viewsets.ViewSet):
    """
    API V2: api/2/uielements/
            api/2/uielements/:id/
    """
    queryset = UIElement.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return UIElement.objects.get(pk=pk)
        except UIElement.DoesNotExist:
            raise Http404("UIElement not found")

    def list(self, request):
        """
        GET api/2/uielements/ - Provides list of UIElements filtered by parameters
        """
        uielements = UIElementFilterSet(request.query_params)
        serializer = serializers.UIElementSerializer(uielements, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/uielements/:id/ - Get UIElement by id
        """
        uielement = self.get_object(pk)
        serializer = serializers.UIElementSerializer(uielement)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/uielements/ - Create a new UIElement
        """
        if 'project_id' in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        if 'uielementname_id' in request.data:
            request.data['uielementname'] = request.data['uielementname_id']
            del request.data['uielementname_id']
        if 'label_text_loc_ids' in request.data:
            request.data['label_text_loc'] = request.data['label_text_loc_ids']
            del request.data['label_text_loc_ids']
        serializer = serializers.UIElementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/uielements/:id/ - Update existing UIElement
        """
        uielement = self.get_object(pk)
        if 'project_id' in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        if 'uielementname_id' in request.data:
            request.data['uielementname'] = request.data['uielementname_id']
            del request.data['uielementname_id']
        if 'label_text_loc_ids' in request.data:
            request.data['label_text_loc'] = request.data['label_text_loc_ids']
            del request.data['label_text_loc_ids']
        serializer = serializers.UIElementSerializer(uielement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/uielements/:id/ - Delete a UIElement
        """
        uielement = self.get_object(pk)
        uielement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UIElementNameViewSet(viewsets.ViewSet):
    """
    API V2: api/2/uielementnames/
            api/2/uielementnames/:id/
    """
    queryset = UIElementName.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return UIElementName.objects.get(pk=pk)
        except UIElementName.DoesNotExist:
            raise Http404("UIElementName not found")

    def list(self, request):
        """
        GET api/2/uielementnames/ - Provides list of UIElementNames filtered by parameters
        """
        uielementnames = UIElementNameFilterSet(request.query_params)
        serializer = serializers.UIElementNameSerializer(uielementnames, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/uielementnames/:id/ - Get UIElementName by id
        """
        uielementname = self.get_object(pk)
        serializer = serializers.UIElementNameSerializer(uielementname)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/uielementnames/ - Create a new UIElementName
        """
        serializer = serializers.UIElementNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/uielementnames/:id/ - Update existing UIElementName
        """
        uielementname = self.get_object(pk)
        serializer = serializers.UIElementNameSerializer(uielementname, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/uielementnames/:id/ - Delete a UIElementName
        """
        uielementname = self.get_object(pk)
        uielementname.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UIGroupViewSet(viewsets.ViewSet):
    """
    API V2: api/2/uigroups/
            api/2/uigroups/:id/
    """
    queryset = UIGroup.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return UIGroup.objects.get(pk=pk)
        except UIGroup.DoesNotExist:
            raise Http404("UIGroup not found")

    def list(self, request):
        """
        GET api/2/uigroups/ - Provides list of UIGroups filtered by parameters
        """
        uigroups = UIGroupFilterSet(request.query_params)
        session = None
        if "session_id" in request.query_params:
            try:
                session = Session.objects.get(pk=request.query_params["session_id"])
            except:
                raise ParseError("Session not found")
        serializer = serializers.UIGroupSerializer(uigroups,
                                                   context={"admin": "admin" in request.query_params,
                                                            "session": session}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/uigroups/:id/ - Get UIGroup by id
        """
        uigroup = self.get_object(pk)
        session = None
        if "session_id" in request.query_params:
            try:
                session = Session.objects.get(pk=request.query_params["session_id"])
            except:
                raise ParseError("Session not found")
        serializer = serializers.UIGroupSerializer(uigroup,
                                                   context={"session": session,
                                                            "admin": "admin" in request.query_params})
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/uigroups/ - Create a new UIGroup
        """
        if "tag_category_id" in request.data:
            request.data['tag_category'] = request.data['tag_category_id']
            del request.data['tag_category_id']
        if "project_id" in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        if "header_text_loc_ids" in request.data:
            request.data['header_text_loc'] = request.data['header_text_loc_ids']
            del request.data['header_text_loc_ids']
        serializer = serializers.UIGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/uigroups/:id/ - Update existing UIGroup
        """
        uigroup = self.get_object(pk)
        if "tag_category_id" in request.data:
            request.data['tag_category'] = request.data['tag_category_id']
            del request.data['tag_category_id']
        if "project_id" in request.data:
            request.data['project'] = request.data['project_id']
            del request.data['project_id']
        if "header_text_loc_ids" in request.data:
            request.data['header_text_loc'] = request.data['header_text_loc_ids']
            del request.data['header_text_loc_ids']
        serializer = serializers.UIGroupSerializer(uigroup, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/uigroups/:id/ - Delete a UIGroup
        """
        uigroup = self.get_object(pk)
        uigroup.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UIItemViewSet(viewsets.ViewSet):
    """
    API V2: api/2/uiitems/
            api/2/uiitems/:id/
    """
    queryset = UIItem.objects.all()
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

    def get_object(self, pk):
        try:
            return UIItem.objects.get(pk=pk)
        except UIItem.DoesNotExist:
            raise Http404("UIItem not found")

    def list(self, request):
        """
        GET api/2/uiitems/ - Provides list of UIItems filtered by parameters
        """
        uiitems = UIItemFilterSet(request.query_params)
        serializer = serializers.UIItemSerializer(uiitems, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/uiitems/:id/ - Get UIItem by id
        """
        uiitem = self.get_object(pk)
        # session_id not needed, because no localization..?
        serializer = serializers.UIItemSerializer(uiitem)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/uiitems/ - Create a new UIItem
        """
        if "ui_group_id" in request.data:
            request.data['ui_group'] = request.data['ui_group_id']
            del request.data['ui_group_id']
        if "tag_id" in request.data:
            request.data['tag'] = request.data['tag_id']
            del request.data['tag_id']
        if "parent_id" in request.data:
            request.data['parent'] = request.data['parent_id']
            del request.data['parent_id']
        serializer = serializers.UIItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/uiitems/:id/ - Update existing UIItem
        """
        uiitem = self.get_object(pk)
        if "ui_group_id" in request.data:
            request.data['ui_group'] = request.data['ui_group_id']
            del request.data['ui_group_id']
        if "tag_id" in request.data:
            request.data['tag'] = request.data['tag_id']
            del request.data['tag_id']
        if "parent_id" in request.data:
            request.data['parent'] = request.data['parent_id']
            del request.data['parent_id']
        serializer = serializers.UIItemSerializer(uiitem, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/uiitems/:id/ - Delete a UIItem
        """
        uiitem = self.get_object(pk)
        uiitem.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ViewSet):
    """
    API V2: api/2/users/
    """
    queryset = User.objects.all()

    def create(self, request):
        """
        POST api/2/user/ - Creates new User based on either device_id or username/pass. Returns token.
        """
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            # try to find user profile:
            try:
                profile = UserProfile.objects.get(device_id=self.request.data["device_id"][:254])
                user = profile.user
                # try to find existing token
                try:
                    token = Token.objects.get(user=profile.user)
                # create a token for this profile
                except Token.DoesNotExist:
                    token = Token.objects.create(user=profile.user)
            # no matching device_id in profiles, create new user
            except UserProfile.DoesNotExist:
                # save the serializer to create new user account
                user = serializer.save()
                # obtain token for this new user
                token = Token.objects.create(user=user)
        return Response({"username": user.username, "token": token.key})


class VoteViewSet(viewsets.ViewSet):
    """
    API V2: api/2/votes/
            api/2/votes/:id/
    """
    queryset = Vote.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Vote.objects.get(pk=pk)
        except Vote.DoesNotExist:
            raise Http404("Vote not found")

    def list(self, request):
        """
        GET api/2/votes/ - Provides list of Votes filtered by parameters
        """
        votes = VoteFilterSet(request.query_params)
        serializer = serializers.VoteSerializer(votes, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET api/2/votes/:id/ - Get Vote by id
        """
        vote = self.get_object(pk)
        serializer = serializers.VoteSerializer(vote)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/votes/ - Create a new Vote
        """
        if "asset_id" in request.data:
            request.data['asset'] = request.data['asset_id']
            del request.data['asset_id']
        if "session_id" in request.data:
            request.data['session'] = request.data['session_id']
            del request.data['session_id']
        if "voter_id" in request.data:
            request.data['voter'] = request.data['voter_id']
            del request.data['voter_id']
        serializer = serializers.VoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        """
        PATCH api/2/votes/:id/ - Update existing Vote
        """
        vote = self.get_object(pk)
        if "asset_id" in request.data:
            request.data['asset'] = request.data['asset_id']
            del request.data['asset_id']
        if "session_id" in request.data:
            request.data['session'] = request.data['session_id']
            del request.data['session_id']
        if "voter_id" in request.data:
            request.data['voter'] = request.data['voter_id']
            del request.data['voter_id']
        serializer = serializers.VoteSerializer(vote, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE api/2/votes/:id/ - Delete a Vote
        """
        vote = self.get_object(pk)
        vote.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
