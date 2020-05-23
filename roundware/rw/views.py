# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import logging

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.views.generic.base import TemplateView
from django.utils.safestring import mark_safe
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from guardian.mixins import PermissionRequiredMixin
from braces.views import (LoginRequiredMixin, FormValidMessageMixin,
                          AjaxResponseMixin)
from extra_views import InlineFormSet
from extra_views.multi import MultiFormView, FormProvider

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


class UIGroupMappingsOrganizationView(SetupTagUIMixin, AjaxResponseMixin,
                                       MultiFormView):
    success_url = '.'
    template_name = 'setup_tag_ui_form.html'
    forms = {
        'ui_group_select': FormProvider(
            UIGroupForSetupTagUISelectForm,
            context_suffix='form',
            init_args={'user': 'get_%s_user'}),

        'ui_group_edit': MultiFormView.modelform(UIGroup,
                                                  UIGroupForSetupTagUIEditForm),

    }

    def get_ui_group_select_user(self):
        return self.request.user

    def get_ui_group_edit_instance(self):
        """ for calling with a primary key in the url. This is called magically
            by MultiFormView to get the instance for ui_group_edit form
        """
        if self.kwargs.get('pk'):
            return UIGroup.objects.filter(pk=self.kwargs['pk'])[0]
        elif self.request.POST.get('ui_group_edit-id', None):
            return UIGroup.objects.filter(
                pk=self.request.POST['ui_group_edit-id'])[0]
        else:
            return UIGroup()

    def post(self, request, *args, **kwargs):
        """ create or update UIGroup instance
        """
        return super(UIGroupMappingsOrganizationView, self).post(request, *args, **kwargs)

    def post_ajax(self, request, *args, **kwargs):
        """ handle post made from selecting UIGroup in 'ui_group_select'
            form. AJAX posts will only result from modelchoicefield select
            for UIGroup changing.
        """
        edit_form_template = 'rw/setup_tags_ui_edit_form.html'
        response_dic = {}

        # if modelchoicefield not empty
        if request.POST.get("ui_group_select-uigroup"):
            id_to_update = request.POST["ui_group_select-uigroup"]
            mui = UIGroup.objects.get(pk=id_to_update)
            edit_form = UIGroupForSetupTagUIEditForm(instance=mui)
            response_dic['mui_update_id'] = mui.id

        else:
            edit_form = UIGroupForSetupTagUIEditForm()

        response_dic['ui_group_edit_form'] = edit_form

        return HttpResponse(render_to_string(edit_form_template,
                                             response_dic,
                                             RequestContext(request)))

    def update_ui_items(self, uiitems, formtags, defaults, indexes, mui):
        uimaptags = []

        default_tags = [df.startswith('t') and Tag.objects.filter(pk=df.replace('t', ''))[0] or
                        UIItem.objects.filter(pk=df)[0].tag for df in defaults]
        for uiitem in uiitems:
            uimaptags.append(uiitem.tag)
            if uiitem.tag not in formtags:
                uiitem.delete()
        for tag in formtags:
            try:
                index = indexes.index(str(tag.pk)) + 1
            except ValueError:
                index = 1
            is_default = tag in default_tags
            if tag not in uimaptags:
                uiitem = UIItem(tag=tag, ui_group=mui, active=True,
                                  index=index, default=is_default)
                uiitem.save()
            else:
                uiitem = [uim for uim in uiitems if uim.tag == tag][0]
                uiitem.index = index
                uiitem.default = is_default
                uiitem.save()

    def valid_all(self, valid_forms):
        """ handle case all forms valid
        """
        select = valid_forms['ui_group_select']  # don't save anything
        select  # pyflakes
        form = valid_forms['ui_group_edit']
        mui_id = form.cleaned_data.get('id')
        formtags = form.cleaned_data['ui_items_tags']

        defaults = form.data['ui_group_edit-ui_items_tag_order'].split(',')
        if form.cleaned_data['ui_items_tags_indexes']:
            indexes = form.cleaned_data['ui_items_tags_indexes'].split(',')
            indexes = [el.startswith('t') and el.replace('t', '') or
                       UIItem.objects.select_related('tag').filter(
                       pk=el)[0].tag.pk for el in indexes]
        else:
            indexes = []
        if mui_id:
            mui = UIGroup.objects.filter(pk=mui_id)[0]
            uiitems = UIItem.objects.select_related(
                'tag').filter(ui_group=mui)
            # instance isn't constructed yet with data from form so we can't
            # use form.save() but have to do the following with construct=True

            save(form, mui, form._meta.fields, 'form changed', True,
                 form._meta.exclude, True)

            self.update_ui_items(uiitems, formtags, defaults, indexes, mui)

        else:
            mui = form.save()
            self.update_ui_items([], formtags, defaults, indexes, mui)

    def invalid_all(self, invalid_forms):
        """ handle case all forms invalid
        """
        self.forms_invalid(invalid_forms)


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
    return render_to_response("tools/asset-map.html")

@login_required
def listen_map(request):
    return render_to_response("tools/listen-map.html")

