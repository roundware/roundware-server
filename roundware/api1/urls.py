# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.


from __future__ import unicode_literals
from django.conf.urls import patterns, url, include
from roundware.api1 import views
import logging
logger = logging.getLogger(__name__)

urlpatterns = patterns('',
    # V1 API
    url(r'^$', 'api1.views.operations'),
    url(r'^auth/', include('rest_framework.urls',
                               namespace='rest_framework')),

    # V1 DRF API - V1 is partially REST.
    url(r'^rest/$', views.APIRootView.as_view()),
    url(r'^rest/asset/$', views.AssetList.as_view(),
        name='api1-asset'),
    url(r'^rest/assetlocation/$', views.AssetLocationList.as_view(),
        name='api1-assetlocation'),
    url(r'^rest/assetlocation/(?P<pk>[0-9]+)/$',
        views.AssetLocationDetail.as_view(),
        name='api1-assetlocation-detail'),
    url(r'^rest/project/$', views.ProjectList.as_view(),
        name='api1-project'),
    url(r'^rest/event/$', views.EventList.as_view(),
        name='api1-event'),
    url(r'^rest/session/$', views.SessionList.as_view(),
        name='api1-session'),
    url(r'^rest/listeninghistoryitem/$',
        views.ListeningHistoryItemList.as_view(),
        name='api1-listeninghistoryitem'),
)
