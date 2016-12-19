# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.conf.urls import url

from roundware.rw import views

urlpatterns = [
    url(r'^tags/batch_add$', views.MultiCreateTagsView.as_view()),
    # url(r'^uigroups/(?P<pk>\d+)/setup_tag_ui/$',
    #    views.SetupTagUIView.as_view()),
    url(r'^uigroups/(?P<pk>\d+)/setup_tag_ui/$',
        views.UIGroupMappingsOrganizationView.as_view()),
    url(r'^uigroups/setup_tag_ui/$',
        views.UIGroupMappingsOrganizationView.as_view()),
    url(r'^uigroups/setup_tag_ui/update_tag_ui_order',
        views.UpdateTagUIOrder.as_view()),
]
