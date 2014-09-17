# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.conf import settings
from django.conf.urls import patterns, url

# Loading static files for debug mode
from django.conf.urls.static import static

from django.conf.urls import include
from django.contrib import admin

# Import V1 DRF REST API
from roundware.rw import views_api1

from adminplus.sites import AdminSitePlus
from ajax_filtered_fields.views import json_index

from roundware.rw import urls as rw_urls

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^dashboard/asset-map$', 'rw.views.asset_map'),
    url(r'^dashboard/$', 'rw.views.chart_views'),

    # V1 API
    url(r'^api/1/$', 'rw.views.main'),
    url(r'^api/1$', 'rw.views.main'),
    # V1 DRF API - V1 is partially REST.
    url(r'^api/1/rest/$', views_api1.APIRootView.as_view()),
    url(r'^api/1/rest/asset/$', views_api1.AssetList.as_view(),
        name='api1-asset'),
    url(r'^api/1/rest/assetlocation/$', views_api1.AssetLocationList.as_view(),
        name='api1-assetlocation'),
    url(r'^api/1/rest/assetlocation/(?P<pk>[0-9]+)/$',
        views_api1.AssetLocationDetail.as_view(),
        name='api1-assetlocation-detail'),
    url(r'^api/1/rest/project/$', views_api1.ProjectList.as_view(),
        name='api1-project'),
    url(r'^api/1/rest/event/$', views_api1.EventList.as_view(),
        name='api1-event'),
    url(r'^api/1/rest/session/$', views_api1.SessionList.as_view(),
        name='api1-session'),
    url(r'^api/1/rest/listeninghistoryitem/$',
        views_api1.ListeningHistoryItemList.as_view(),
        name='api1-listeninghistoryitem'),

    # V2 RESTful DRF API
    url(r'^api/2/', include('api2.urls')),

    # Use Django Admin login as overall login
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'admin/login.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^rw/', include(rw_urls)),

    # can't use ajax_filtered_fields' urls.py since it relies on old default
    # urls import
    url(r'^ajax_filtered_fields/json_index/$', json_index),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add DRF auth URLs
urlpatterns += patterns('',
    url(r'^api/1/auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
