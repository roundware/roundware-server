#***********************************************************************************#

# ROUNDWARE
# a contributory, location-aware media platform

# Copyright (C) 2008-2014 Halsey Solutions, LLC
# with contributions from:
# Mike MacHenry, Ben McAllister, Jule Slootbeek and Halsey Burgund (halseyburgund.com)
# http://roundware.org | contact@roundware.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.html>.

#***********************************************************************************#


from django.conf import settings  #, urls
from django.conf.urls import patterns, url, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from tastypie.api import Api
from roundware.rw.api import AssetResource, SessionResource, EventResource, ProjectResource, ListeningHistoryItemResource, AssetLocationResource

from adminplus.sites import AdminSitePlus
from ajax_filtered_fields.views import json_index

from roundware.rw import urls as rw_urls

# from roundware.rw import forms

admin.site = AdminSitePlus()
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(AssetResource())
v1_api.register(AssetLocationResource())
v1_api.register(ProjectResource())
v1_api.register(EventResource())
v1_api.register(SessionResource())
v1_api.register(ListeningHistoryItemResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'roundware.views.home', name='home'),
#    url(r'^charts/asset/$', 'rw.views.chart_views'),
    url(r'^dashboard/asset-map$', 'rw.views.asset_map'),
    url(r'^dashboard/$', 'rw.views.chart_views'),

    #TastyPie API URLS
    url(r'^roundware/api/', include(v1_api.urls)),

    url(r'^roundware/$', 'rw.views.main'),
    url(r'^roundware$', 'rw.views.main'),

    # use admin login as overall login
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'admin/login.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^rw/', include(rw_urls)),

    # can't use ajax_filtered_fields' urls.py since it relies on old default
    # urls import
    url(r'^ajax_filtered_fields/json_index/$', json_index),
) 

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )
    except:
        pass


