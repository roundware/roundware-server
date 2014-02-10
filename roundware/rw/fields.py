from django.forms import forms
from south.modelsinspector import add_introspection_rules
from validatedfile.fields import ValidatedFileField
from sortedm2m.forms import SortedMultipleChoiceField


class RWValidatedFileField(ValidatedFileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. 
        Example: ['application/pdf', 'image/jpeg']
    """
    def __init__(self, content_types=None, **kwargs):
        if content_types:
            self.content_types = content_types

        super(RWValidatedFileField, self).__init__(**kwargs)

    def clean(self, *args, **kwargs):        
        # ValidatedFileField.clean will check the MIME type from the 
        # http headers and by peeking in the file
        data = super(RWValidatedFileField, self).clean(*args, **kwargs)

        file = data.file

        # next scan with pyclamav
        tmpfile = file.file.name
        import pyclamav  # keep this import here to not slow down streamscript
        has_virus, virus_name = pyclamav.scanfile(tmpfile)
        if has_virus:
            fn = file.name
            raise forms.ValidationError(
                'The file %s you uploaded appears to contain a virus or be'
                'malware (%s).' % (fn, virus_name)
            )
            
        return data


add_introspection_rules([], ["^roundware\.rw\.fields\.RWValidatedFileField"])        


class RWTagOrderingSortedMultipleChoiceField(SortedMultipleChoiceField):

    def clean(self, value):
        """ our hack involves stuffing values starting with t for tags that
            need to be turned into new UIMappings into this field
        """
        value = [v for v in value if not v.startswith('t')]
        super(RWTagOrderingSortedMultipleChoiceField, self).clean(value)
        