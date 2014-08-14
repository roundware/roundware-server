# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# The Django REST Framework object serializers for the V2 API.
from __future__ import unicode_literals
from roundware.rw.models import Asset, Project, Event, Session, ListeningHistoryItem
from rest_framework import serializers

class AssetSerializer(serializers.ModelSerializer):
    audiolength_in_seconds = serializers.FloatField()
    class Meta:
        model = Asset
