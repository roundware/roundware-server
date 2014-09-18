# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework Views for the V2 API.
from roundware.rw.models import (Asset, Event, ListeningHistoryItem, Project,
                                 Session, Tag)
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework import viewsets
import serializers
from permissions import AuthenticatedReadAdminWrite


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
    serializer_class = serializers.Asset
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
    serializer_class = serializers.Event
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
    serializer_class = serializers.ListenEvent
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
    serializer_class = serializers.Project
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

class SessionViewSet(viewsets.ModelViewSet):
    """
    API V2: api/2/sessions/:session_id

    <Permissions>
    Anonymous: None.
    Authenticated: GET/POST/PUT/PATCH for objects owned by user.
    Admin: GET/POST/PUT/PATCH.
    """
    queryset = Session.objects.all()
    serializer_class = serializers.Session
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
    serializer_class = serializers.Tag
    permission_classes = (IsAuthenticated, AuthenticatedReadAdminWrite)

