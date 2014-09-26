# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.conf import settings
from django.conf.urls import patterns, url

# Loading static files for debug mode
from django.conf.urls.static import static

from django.conf.urls import include
from django.contrib import admin

from adminplus.sites import AdminSitePlus
from ajax_filtered_fields.views import json_index

from roundware.rw import urls as rw_urls

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^dashboard/asset-map$', 'rw.views.asset_map'),
    url(r'^dashboard/$', 'rw.views.chart_views'),

    # V1 DRF API
    url(r'^api/1/', include('api1.urls')),
    # V2 RESTful DRF API
    url(r'^api/2/', include('api2.urls')),

    # Use Django Admin login as overall login
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'admin/login.html'}),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^rw/', include(rw_urls)),

    # can't use ajax_filtered_fields' urls.py since it relies on old default
    # urls import
    url(r'^ajax_filtered_fields/json_index/$', json_index),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
