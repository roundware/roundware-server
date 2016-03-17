# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.conf.urls import patterns, url

from roundware.rw import views

urlpatterns = patterns(
    '',
    url(r'^tags/batch_add$', views.MultiCreateTagsView.as_view()),
    # url(r'^masteruis/(?P<pk>\d+)/setup_tag_ui/$',
    #    views.SetupTagUIView.as_view()),
    url(r'^masteruis/(?P<pk>\d+)/setup_tag_ui/$',
        views.MasterUIMappingsOrganizationView.as_view()),
    url(r'^masteruis/setup_tag_ui/$',
        views.MasterUIMappingsOrganizationView.as_view()),
    url(r'^masteruis/setup_tag_ui/update_tag_ui_order',
        views.UpdateTagUIOrder.as_view()),
)
