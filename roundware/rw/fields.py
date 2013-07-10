from django.db.models import FileField, IntegerField
from django.forms import forms
from django.utils.translation import ugettext_lazy as _
from south.modelsinspector import add_introspection_rules


class BigIntegerField(IntegerField):
    empty_strings_allowed = False

    def get_internal_type(self):
        return "BigIntegerField"

    def db_type(self):
        return 'bigint'  # Note this won't work with Oracle.


class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. 
        Example: ['application/pdf', 'image/jpeg']
        This is not reliable outside of controlled users since content_type
        can be spoofed.
    """
    def __init__(self, content_types=None, **kwargs):
        if content_types:
            self.content_types = content_types

        super(ContentTypeRestrictedFileField, self).__init__(**kwargs)

    def clean(self, *args, **kwargs):        
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        if self.content_types:
            try:
                content_type = file.content_type
                if content_type not in self.content_types:
                    raise forms.ValidationError(_('Filetype not supported.'))
            except AttributeError:
                pass        
            
        return data


add_introspection_rules([], ["^roundware\.rw\.fields\.ContentTypeRestrictedFileField"])        
