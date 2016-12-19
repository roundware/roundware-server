# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.conf import settings
from django.conf.urls import url

# Loading static files for debug mode
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from django.conf.urls import include
from django.contrib import admin

from adminplus.sites import AdminSitePlus

from roundware.rw import urls as rw_urls

from roundware.rw import views as rw_views

admin.site = AdminSitePlus()
admin.sites.site = admin.site
admin.autodiscover()

urlpatterns = [
    url(r'^tools/asset-map$', rw_views.asset_map),
    url(r'^tools/listen-map$', rw_views.listen_map),
    url(r'^dashboard/$', rw_views.chart_views),

    # V1 DRF API
    url(r'^api/1/', include('roundware.api1.urls')),
    # V2 RESTful DRF API
    url(r'^api/2/', include('roundware.api2.urls')),

    # Use Django Admin login as overall login
    url(r'^accounts/login/$', auth_views.login,
        {'template_name': 'admin/login.html'}),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^rw/', include(rw_urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Roundware Administration'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
