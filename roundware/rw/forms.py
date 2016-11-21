# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.forms.models import BaseModelFormSet

import floppyforms as forms
from crispy_forms.helper import FormHelper
from guardian.shortcuts import get_objects_for_user

from django.conf import settings

from roundware.rw.models import Tag, UIGroup, UIItem
from roundware.rw import fields
from roundware.rw.widgets import (NonAdminRelatedFieldWidgetWrapper,
                                  DummyWidgetWrapper,
                                  SetupTagUIFilteredSelectMultiple,
                                  SetupTagUISortedCheckboxSelectMultiple)


def get_formset_media_js():
    """
    """
    FORMSET_FULL = settings.STATIC_URL + 'js/jquery.formset.js'
    FORMSET_MINIFIED = settings.STATIC_URL + 'rw/js/jquery.formset.min.js'
    formset_js_path = FORMSET_FULL if settings.DEBUG else FORMSET_MINIFIED
    formset_media_js = (formset_js_path, )
    return formset_media_js


class TagCreateForm(forms.ModelForm):

    """ Custom create form for tags allowing batch creation of Tags assigned
        to a TagCategory
    """

    msg_rel = Tag.loc_msg.through

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = 'bootstrap3/table_inline_formset.html'
        # self.helper.add_input(Submit('submit', 'Save All'))
        super(TagCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Tag
        fields = ['tag_category']  # formset in multiview adds others
        widgets = {  # floppyforms requires override orig widgets to use theirs
            'tag_category': forms.Select,
            'value': forms.TextInput,
            'description': forms.TextInput,
            'data': forms.TextInput,
            'loc_msg': NonAdminRelatedFieldWidgetWrapper(
                forms.SelectMultiple(attrs={}),
                '/admin/rw/localizedstring/add')
        }
        labels = {
            'loc_msg': "Localized Text"
        }

    class Media:
        js = get_formset_media_js() + \
            ('admin/js/admin/RelatedObjectLookups.js',)
        css = {'all': ('rw/css/tag_batch_add.css',)}


class BatchTagFormset(BaseModelFormSet):

    def save(self):
        """ saving is handled by view.  May need to revisit this if we
        add inlines.
        """
        pass

    # XXX TODO: if we decide to add localized messages inline we can use below
    # as a start.
    # def add_fields(self, form, index):
    #     """ add custom fields for entry of localized string text and language.
    #         Can't use an inlineformset since the field loc_msg is manytomany.
    #     """
    #     super(BatchTagFormset, self).add_fields(form, index)
    #     form.fields["localized_text"] = forms.CharField()
    #     form.fields["loc_txt_language"] = forms.ModelChoiceField(Language.objects.all())


class UIGroupForSetupTagUIFormMixin(object):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.template = 'bootstrap3/whole_uni_form.html'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        # self.helper.add_input(Submit('submit', 'Save All'))
        super(UIGroupForSetupTagUIFormMixin, self).__init__(*args, **kwargs)


class UIGroupForSetupTagUICreateForm(UIGroupForSetupTagUIFormMixin,
                                      forms.ModelForm):

    class Meta:
        model = UIGroup
        fields = ['project']
        widgets = {  # floppyforms requires override orig widgets to use theirs
            'project': forms.Select,
        }


class UIGroupForSetupTagUISelectForm(UIGroupForSetupTagUIFormMixin,
                                      forms.Form):

    """ form for selection of UIGroups for editing form
    """
    uigroup = forms.ModelChoiceField(
        queryset=UIGroup.objects.all().order_by('id'),
        required=False,
        widget=forms.Select(attrs={"onChange": 'update_UIGroup_edit_form()'}),
        label='UI Group',
        help_text='Leave blank to add a new UI Group or select one to edit',
        empty_label="---------")

    def __init__(self, user, *args, **kwargs):
        super(UIGroupForSetupTagUISelectForm, self).__init__(*args, **kwargs)
        self.helper.form_id = 'mui_select_form'
        self.prefix = 'ui_group_select'
        self.fields['uigroup'].queryset = \
            UIGroup.objects.filter(project__in=get_objects_for_user(user,
                                                                     'rw.access_project')
                                    ).order_by('id')

    def form_valid(self):
        return True
        pass


class UIGroupForSetupTagUIEditForm(UIGroupForSetupTagUIFormMixin,
                                    forms.ModelForm):

    id = forms.IntegerField(required=False,  # store pk on UIGroup for update
                            widget=forms.HiddenInput)

    ui_items_tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        label='Assign tags',
        required=False,
        widget=NonAdminRelatedFieldWidgetWrapper(
            SetupTagUIFilteredSelectMultiple('tags', False),
            '/admin/rw/tag/add')
    )

    ui_items_tag_order = fields.RWTagOrderingSortedMultipleChoiceField(
        queryset=UIItem.objects.none(),
        label='Order and assign default tags',
        required=False,
        widget=DummyWidgetWrapper(
            SetupTagUISortedCheckboxSelectMultiple()
        )
    )

    ui_items_tags_indexes = forms.CharField(
        widget=forms.HiddenInput,
        required=False)

    def __init__(self, *args, **kwargs):

        super(UIGroupForSetupTagUIEditForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        self.prefix = 'ui_group_edit'
        if 'instance' in kwargs:
            self.instance = kwargs['instance']
            uiitems = UIItem.objects.select_related('tag').filter(
                ui_group=self.instance).order_by('index')
            self.initial['ui_items_tags'] = [
                uiitem.tag.id for uiitem in uiitems]
            # self.initial['ui_items_tag_order'] = []
            self.fields['ui_items_tag_order'].queryset = uiitems
            self.fields['ui_items_tag_order'].label_from_instance = \
                self.get_order_instance_label
            self.initial['ui_items_tag_order'] = [uiitem.id for uiitem
                                                     in uiitems if uiitem.default]

    def get_order_instance_label(self, obj):
        return obj.tag.__unicode__()

    def is_valid(self):
        return super(UIGroupForSetupTagUIEditForm, self).is_valid()

    class Media:
        # load the setup_tag_ui.js in the selectmultiple widget so it loads
        # early enough.
        js = get_formset_media_js() + \
            ('admin/js/admin/RelatedObjectLookups.js', )

        css = {'all': ('rw/css/setup_tag_ui.css',)}

    class Meta:
        model = UIGroup
        fields = ['id', 'project', 'ui_mode', 'tag_category', 'select',
                  'active', 'index', 'name', 'header_text_loc',
                  'ui_items_tags', 'ui_items_tag_order',
                  ]
        widgets = {  # floppyforms requires override orig widgets to use theirs
            'id': forms.HiddenInput,
            'project': forms.Select,
            'ui_mode': forms.Select,
            'tag_category': forms.Select,
            'select': forms.Select,
            'active': forms.CheckboxInput,
            'index': forms.NumberInput,
            'name': forms.TextInput,
            'header_text_loc': NonAdminRelatedFieldWidgetWrapper(
                forms.SelectMultiple(attrs={}),
                '/admin/rw/localizedstring/add'),
        }
        labels = {
            'ui_mode': 'Mode',
            'tag_category': 'Category',
            'select': 'Select Type',
            'index': 'Ordering',
            'header_text_loc': "Localized Header Text",
        }
