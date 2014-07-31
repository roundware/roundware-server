# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
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

        # ClamAV scan was here. See:
        # https://github.com/hburgund/roundware-server/issues/107

        return data


add_introspection_rules([], ["^roundware\.rw\.fields\.RWValidatedFileField"])


class RWTagOrderingSortedMultipleChoiceField(SortedMultipleChoiceField):

    def clean(self, value):
        """ our hack involves stuffing values starting with t for tags that
            need to be turned into new UIMappings into this field
        """
        value = [v for v in value if not v.startswith('t')]
        super(RWTagOrderingSortedMultipleChoiceField, self).clean(value)
