# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework Views for the V2 API.
from roundware.rw.models import Asset, Project, Event, Session, ListeningHistoryItem
from serializers import (AssetSerializer)
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions
import django_filters

class APIRootView(APIView):
    """
    The V2 API root view listing available endpoints 
    """
    def get(self, request, format=None):
        # The endpoints use the 'api2:' URL namespace.
        data = {
           'assets': reverse('api2:assets', request=request, format=format),

        }
        return Response(data)


class AssetList(generics.ListAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filter_class = AssetFilter
