# from django.views.generic import CreateView
from django.forms.models import (modelformset_factory, BaseModelFormSet,                                  
                                 inlineformset_factory)

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.utils import render_crispy_form
from braces.views import LoginRequiredMixin
from djangoformsetjs.utils import formset_media_js


from roundware.rw.models import Tag, LocalizedString


class TagCreateForm(forms.ModelForm):
    """ Custom create form for tags allowing batch creation of Tags assigned
        to a TagCategory
    """

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
            # 'loc_msg': forms.URLInput,  # temporary comment... will be inline
        }

    class Media:
        js = formset_media_js
        css = {'all': ('rw/css/tag_batch_add.css',)}
      

# TagLocalizedStringFormset = inlineformset_factory(Tag, LocalizedString,
#     fields=('localized_string', 'language'), can_delete=True)
