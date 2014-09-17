# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework Views for the V2 API.
from roundware.rw.models import Asset, Project, Event, Session, ListeningHistoryItem
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework import viewsets
from serializers import AssetSerializer


class AssetViewSet(viewsets.ModelViewSet):
    """
    API V2: api/2/assets/:asset_id

    <Permissions>
    Anonymous: None.
    Authenticated: GET. PUT/PATCH/DELETE for objects owned by user. 
    Admin: GET/POST/PUT/PATCH/DELETE.
    """

    # TODO: Implement DjangoObjectPermissions
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (IsAuthenticated, DjangoObjectPermissions)
