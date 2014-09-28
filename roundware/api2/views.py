# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework Views for the V2 API.
from __future__ import unicode_literals
from roundware.rw.models import (Asset, Event, ListeningHistoryItem, Project,
                                 Session, Tag)
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework import viewsets
import serializers
from permissions import AuthenticatedReadAdminWrite
import logging

logger = logging.getLogger(__name__)

# TODO: http://www.django-rest-framework.org/api-guide/relations#hyperlinkedrelatedfield

# Note: Keep this stuff in alphabetical order!

class AssetViewSet(viewsets.ModelViewSet):
    """
    API V2: api/2/assets/:asset_id

    <Permissions>
    Anonymous: None.
    Authenticated: GET/POST. PUT/PATCH/DELETE for objects owned by user. 
    Admin: GET/POST/PUT/PATCH/DELETE.
    """

    # TODO: Implement DjangoObjectPermissions
    queryset = Asset.objects.all()
    serializer_class = serializers.AssetSerializer
    permission_classes = (IsAuthenticated, DjangoObjectPermissions)

class EventViewSet(viewsets.ModelViewSet):
    """
    API V2: api/2/events/:event_id

    <Permissions>
    Anonymous: None.
    Authenticated: GET/POST 
    Admin: GET/POST
    """

    # TODO: Implement ViewCreate permission.
    queryset = Event.objects.all()
    serializer_class = serializers.EventSerializer
    permission_classes = (IsAuthenticated,)

class ListenEventViewSet(viewsets.ModelViewSet):
    """
    API V2: api/2/listenevents/:listenevent_id

    <Permissions>
    Anonymous: None.
    Authenticated: GET/POST.
    Admin: GET/POST.
    """

    # TODO: Implement ViewCreate permission.
    # TODO: Rename ListeningHistoryItem model to ListenEvent.
    queryset = ListeningHistoryItem.objects.all()
    serializer_class = serializers.ListenEventSerializer
    permission_classes = (IsAuthenticated,)

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API V2: api/2/projects/:project_id

    <Permissions>
    Anonymous: None.
    Authenticated: GET.
    Admin: GET/POST/PUT/PATCH/DELETE.
    """
    # TODO: Return messages in response
    queryset = Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

class StreamViewSet(viewsets.ViewSet):
    """
    The primary communication channel for handling the Roundware audio stream.
    Only one stream per user id/token so the end point is not plural.
    API V2: api/2/stream/

    <Permissions>
    Anonymous: None.
    Authenticated: GET/POST/PUT/PATCH for the user specific stream.
    Admin: GET/POST/PUT/PATCH for the user specific stream.
    """
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        GET api/2/stream/ - Gets information about an existing stream
        """
        # Validate the input
        serializer = serializers.StreamSerializer(data=request.GET)
        if not serializer.is_valid():
            raise ParseError(serializer.errors)

        # TODO: Return data about the stream, only if it exists.

        return Response(serializer.data)


    def create(self, request):
        serializer = serializers.StreamSerializer()
        return Response(serializer.data)


class SessionViewSet(viewsets.ModelViewSet):
    """
    API V2: api/2/sessions/:session_id

    <Permissions>
    Anonymous: None.
    Authenticated: GET/POST/PUT/PATCH for objects owned by user.
    Admin: GET/POST/PUT/PATCH.
    """
    queryset = Session.objects.all()
    serializer_class = serializers.SessionSerializer
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

class TagViewSet(viewsets.ModelViewSet):
    """
    API V2: api/2/tags/:tag_id

    <Permissions>
    Anonymous: None.
    Authenticated: GET.
    Admin: GET/POST/PUT/PATCH/DELETE.
    """
    # TODO: Return messages and relationships in response
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

