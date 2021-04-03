# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import logging

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.views.generic.base import TemplateView
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from guardian.mixins import PermissionRequiredMixin
from braces.views import (LoginRequiredMixin, FormValidMessageMixin,
                          AjaxResponseMixin)
from extra_views import InlineFormSet

from roundware.rw.models import Tag, UIGroup, UIItem, Project
from roundware.rw.forms import (TagCreateForm, BatchTagFormset,
                                UIGroupForSetupTagUIEditForm,
                                UIGroupForSetupTagUISelectForm)
from roundware.rw.widgets import SetupTagUISortedCheckboxSelectMultiple
logger = logging.getLogger(__name__)


class UIItemsInline(InlineFormSet):
    model = UIItem
    fk_name = 'ui_group'


class SetupTagUIMixin(LoginRequiredMixin, PermissionRequiredMixin):

    """ make sure User can modify this UIGroup based on Project,
        and is logged in.
    """
    permission_required = 'rw.access_project'
    return_403 = True

    def get_object(self):
        """ return Project for this UIGroup  as the object to check against
        """
        try:
            return get_object_or_404(Project, uigroup=self.kwargs['pk'])
        except KeyError:
            return None

class UpdateTagUIOrder(TemplateView):

    """ display the widget for the ui_group_edit_tag_order field as updated
        based on the value of the ui_group_edit_tags field on
        UIGroupMappingsOrganizationView edit form.
    """

    def __init__(self, **kwargs):
        self.widget = SetupTagUISortedCheckboxSelectMultiple()

    def choice_iterator(self):
        for uiitem in self.queryset:
            yield (uiitem.pk, uiitem.tag.__unicode__())

    def post(self, request, *args, **kwargs):
        """ add or remove checkbox items to the order field based on contents
            of the ui_group_edit_tags field.  UIItems may not exist
            corresponding to the chosen tag.  UIItems will never exist for
            a newly created UIGroup.
        """

        tag_vals = [Tag.objects.filter(pk=t)[0] for t in request.POST.getlist(
            'tags[]')]
        mui = request.POST.getlist('mui')[0]

        if mui:
            self.queryset = UIItem.objects.select_related('tag'
                                                             ).filter(ui_group__pk=mui, tag__in=tag_vals).order_by('index')
            filtered = self.queryset.filter(default=True)
        else:
            self.queryset = UIItem.objects.none()
            filtered = self.queryset

        # if tag id in request is not present in queryset, then we need to
        # create a line in the widget for a new empty uiitem.  Store the
        # tag id in a hidden field on the widget
        tags_seen = [map.tag for map in self.queryset]
        tags_unseen = [t for t in tag_vals if t not in tags_seen]

        html = self.widget.render('ui_group_edit-ui_items_tag_order',
                                  value=[uiitem.pk for uiitem in filtered],
                                  attrs={
                                      'id': 'id_ui_group_edit-ui_items_tag_order'},
                                  choices=self.choice_iterator(),
                                  new_maps=tags_unseen,)
        return HttpResponse(mark_safe(html))


@login_required
def asset_map(request):
    return render(None, "tools/asset-map.html")

@login_required
def listen_map(request):
    return render(None, "tools/listen-map.html")
