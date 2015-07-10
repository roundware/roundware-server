# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from sortedm2m.forms import SortedMultipleChoiceField


class RWTagOrderingSortedMultipleChoiceField(SortedMultipleChoiceField):

    def clean(self, value):
        """ our hack involves stuffing values starting with t for tags that
            need to be turned into new UIMappings into this field
        """
        value = [v for v in value if not v.startswith('t')]
        super(RWTagOrderingSortedMultipleChoiceField, self).clean(value)
