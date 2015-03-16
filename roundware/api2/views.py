# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework Views for the V2 API.
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from roundware.rw.models import (Asset, Event, ListeningHistoryItem, Project,
                                 Session, Tag, UserProfile, Envelope, Language)
from roundware.api2 import serializers
from roundware.api2.permissions import AuthenticatedReadAdminWrite
from roundware.lib.api import (get_project_tags, modify_stream, move_listener, heartbeat,
                               skip_ahead, add_asset_to_envelope, get_current_streaming_asset,
                               assets_by_query_params, save_asset_from_request, vote_asset,
                               vote_count_by_asset)
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.authtoken.models import Token
from rest_framework.decorators import detail_route
import logging

logger = logging.getLogger(__name__)

# TODO: http://www.django-rest-framework.org/api-guide/relations#hyperlinkedrelatedfield

# Note: Keep this stuff in alphabetical order!


class AssetViewSet(viewsets.ViewSet):
    """
    API V2: api/2/assets/:asset_id

    <Permissions>
    Anonymous: None
    Authenticated: GET/POST.
    Admin: None
    """

    # TODO: Implement DjangoObjectPermissions
    queryset = Asset.objects.all()
    permission_classes = (IsAuthenticated, DjangoObjectPermissions)

    def retrieve(self, request, pk=None):
        """
        GET api/2/assets/:id/
        """
        try:
            asset = Asset.objects.get(pk=pk)
        except Asset.DoesNotExist:
            raise NotFound("Asset not found")
        serializer = serializers.AssetSerializer(asset)
        return Response(serializer.data)

    def create(self, request):
        """
        POST api/2/assets/ - Create a new asset
        """
        if "session_id" not in request.data:
            raise ParseError("session_id required")

        try:
            session_id = int(request.data["session_id"])
            session = Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            raise NotFound("Session not found")

        if "asset_id" not in request.data and "file" not in request.data:
            raise ParseError("Must supply either asset_id or file")

        asset = None
        if "asset_id" in request.data:
            try:
                asset_id = int(request.data["asset_id"])
                asset = Asset.objects.get(pk=asset_id)
            except ValueError, Asset.DoesNotExist:
                raise NotFound("Asset with id %s not found" % request.data["asset_id"])
        asset = save_asset_from_request(request, session, asset)
        return Response({"asset_id": asset.pk})

    def list(self, request):
        """
        GET api/2/assets/ - retrieve list of assets filtered by parameters
        """
        assets = assets_by_query_params(request)
        serializer = serializers.AssetSerializer(assets, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post', 'get'])
    def votes(self, request, pk=None):
        if request.method == "POST":
            vote_op = vote_asset(request, asset_id=pk)
            vote = vote_op["vote"]
            serializer = serializers.VoteSerializer(vote)
            return Response(serializer.data)
        else:
            count = vote_count_by_asset(pk)
            return Response(count)

# class EventViewSet(viewsets.ModelViewSet):
#     """
#     API V2: api/2/events/:event_id

#     <Permissions>
#     Anonymous: None.
#     Authenticated: GET/POST
#     Admin: GET/POST
#     """

#     # TODO: Implement ViewCreate permission.
#     queryset = Event.objects.all()
#     serializer_class = serializers.EventSerializer
#     permission_classes = (IsAuthenticated,)


# class ListenEventViewSet(viewsets.ModelViewSet):
#     """
#     API V2: api/2/listenevents/:listenevent_id

#     <Permissions>
#     Anonymous: None.
#     Authenticated: GET/POST.
#     Admin: GET/POST.
#     """

#     # TODO: Implement ViewCreate permission.
#     # TODO: Rename ListeningHistoryItem model to ListenEvent.
#     queryset = ListeningHistoryItem.objects.all()
#     serializer_class = serializers.ListenEventSerializer
#     permission_classes = (IsAuthenticated,)


class EnvelopeViewSet(viewsets.ViewSet):
    """
    API V2: api/2/users/:user_id

    <Permissions>
    Anonymous: POST
    Authenticated: None
    Admin: None
    """
    queryset = Envelope.objects.all()

    def create(self, request):
        """
        POST api/2/envelopes/ - Creates a new envelope based on passed session_id
        """
        serializer = serializers.EnvelopeSerializer(data=request.data)
        if serializer.is_valid():
            envelope = serializer.save()
            return Response({"envelope_id": envelope.pk})
        else:
            return Response(serializer.errors)

    def partial_update(self, request, pk=None):
        """
        PATCH api/2/envelopes/:id/ - Adds an asset to the envelope
        """
        if "asset_id" in request.data or "file" in request.FILES:
            try:
                result = add_asset_to_envelope(request, envelope_id=pk)
            except Exception as e:
                return Response({"detail": str(e)}, status.HTTP_400_BAD_REQUEST)
            return Response({"asset_id": result["asset_id"]})
        else:
            raise ParseError("asset_id or file required")


class ProjectViewSet(viewsets.ViewSet):
    """
    API V2:

    api/2/projects/:project_id
    <Permissions>
    Anonymous: None
    Authenticated: GET
    Admin: None

    api/2/projects/:project_id/tags
    <Permissions>
    Anonymous: None
    Authenticated: GET
    Admin: None
    """
    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated, )

    def retrieve(self, request, pk=None):
        if "session_id" in request.query_params:
            session = get_object_or_404(Session, pk=request.query_params["session_id"])
            project = get_object_or_404(Project, pk=pk)
            serializer = serializers.ProjectSerializer(project,
                                                       context={"session": session})
        else:
            raise ParseError("session_id parameter is required")
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        if "session_id" in request.query_params:
            session = get_object_or_404(Session, pk=request.query_params["session_id"])
            tags = get_project_tags(s=session)
        else:
            raise ParseError("session_id is required")
            project = get_object_or_404(Project, pk=pk)
            tags = get_project_tags(p=project)
        return Response(tags)

    @detail_route(methods=['get'])
    def assets(self, request, pk=None):
        assets = assets_by_query_params(request, project_id=pk)
        # serialize and return
        serializer = serializers.AssetSerializer(assets, many=True)
        return Response(serializer.data)


class SessionViewSet(viewsets.ViewSet):
    """
    API V2: api/2/sessions/:session_id

    <Permissions>
    Anonymous: None
    Authenticated: GET/POST/PUT/PATCH for objects owned by user.
    Admin: None
    """
    queryset = Session.objects.all()
    permission_classes = (IsAuthenticated, )

    def create(self, request):
        serializer = serializers.SessionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StreamViewSet(viewsets.ViewSet):
    """
    The primary communication channel for handling the Roundware audio stream.
    Only one stream per user id/token so the end point is not plural.
    API V2: api/2/streams/

    <Permissions>
    Anonymous: None
    Authenticated: POST for the user specific stream.
    Admin: None
    """
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        serializer = serializers.StreamSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            raise ParseError(serializer.errors)
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
    def next(self, request, pk=None):
        try:
            skip_ahead(request, session_id=pk)
            return Response()
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def current(self, request, pk=None):
        try:
            result = get_current_streaming_asset(request, session_id=pk)
            return Response(result)
        except Exception as e:
            return Response({"detail": str(e)},
                            status.HTTP_400_BAD_REQUEST)

# class TagViewSet(viewsets.ModelViewSet):
#     """
#     API V2: api/2/tags/:tag_id

#     <Permissions>
#     Anonymous: None.
#     Authenticated: GET.
#     Admin: GET/POST/PUT/PATCH/DELETE.
#     """
#     # TODO: Return messages and relationships in response
#     queryset = Tag.objects.all()
#     serializer_class = serializers.TagSerializer
#     permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)


class UserViewSet(viewsets.ViewSet):
    """
    API V2: api/2/users/:user_id

    <Permissions>
    Anonymous: POST
    Authenticated: None
    Admin: None
    """
    queryset = User.objects.all()

    def create(self, request):
        """
        POST api/2/user/ - Creates new user based on either device_id or username/pass. Returns token
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
