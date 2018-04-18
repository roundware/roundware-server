# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.


from __future__ import unicode_literals
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as rest_framework_views
from roundware.api2 import views
import logging
logger = logging.getLogger(__name__)


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'assets', views.AssetViewSet)
router.register(r'audiotracks', views.AudiotrackViewSet)
router.register(r'envelopes', views.EnvelopeViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'languages', views.LanguageViewSet)
router.register(r'listenevents', views.ListenEventViewSet)
router.register(r'localizedstrings', views.LocalizedStringViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'projectgroups', views.ProjectGroupViewSet)
router.register(r'sessions', views.SessionViewSet)
router.register(r'speakers', views.SpeakerViewSet)
router.register(r'streams', views.StreamViewSet, base_name="Stream")
router.register(r'tags', views.TagViewSet)
router.register(r'tagcategories', views.TagCategoryViewSet)
router.register(r'tagrelationships', views.TagRelationshipViewSet)
router.register(r'timedassets', views.TimedAssetViewSet)
router.register(r'uigroups', views.UIGroupViewSet)
router.register(r'uiitems', views.UIItemViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'votes', views.VoteViewSet)

urlpatterns = [
	url(r'^login/$', rest_framework_views.obtain_auth_token, name='login'),
    url(r'^', include(router.urls)),
]
