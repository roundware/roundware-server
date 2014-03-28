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


from django.conf.urls import patterns, url

from roundware.rw import views

urlpatterns = patterns('',
     url(r'^tags/batch_add$', views.MultiCreateTagsView.as_view()),
     # url(r'^masteruis/(?P<pk>\d+)/setup_tag_ui/$', 
     #    views.SetupTagUIView.as_view()),   
     url(r'^masteruis/(?P<pk>\d+)/setup_tag_ui/$', 
        views.MasterUIMappingsOrganizationView.as_view()),   
     url(r'^masteruis/setup_tag_ui/$', 
        views.MasterUIMappingsOrganizationView.as_view()),  
     url(r'^masteruis/setup_tag_ui/update_tag_ui_order',
        views.UpdateTagUIOrder.as_view() ), 

)