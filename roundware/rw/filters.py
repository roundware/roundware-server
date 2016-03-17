# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.contrib.admin import DateFieldListFilter, RelatedFieldListFilter
from django.contrib.admin.util import (get_model_from_relation,
                                       prepare_lookup_value)
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode

from roundware.rw.models import Tag, TagCategory


class AudiolengthListFilter(DateFieldListFilter):

    """ Provide a filter by audiolength, grouped by ranges.
    """
    # Use DateFieldListFilter base class since it gives us gt/lt ranges

    parameter_name = 'audiolength'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super(AudiolengthListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

        self.field_generic = '%s__' % field_path
        self.date_params = dict([(k, v) for k, v in params.items()
                                 if k.startswith(self.field_generic)])

        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_until = '%s__lt' % field_path
        self.links = (
            (_('Any'), {}),
            (_('< 10s'), {
                self.lookup_kwarg_since: 0,
                self.lookup_kwarg_until: 10000000000,
            }),
            (_('10s - 20s'), {
                self.lookup_kwarg_since: 10000000000,
                self.lookup_kwarg_until: 20000000000,
            }),
            (_('20s - 30s'), {
                self.lookup_kwarg_since: 20000000000,
                self.lookup_kwarg_until: 30000000000,
            }),
            (_('30s - 40s'), {
                self.lookup_kwarg_since: 30000000000,
                self.lookup_kwarg_until: 40000000000,
            }),
            (_('40s - 50s'), {
                self.lookup_kwarg_since: 40000000000,
                self.lookup_kwarg_until: 50000000000,
            }),
            (_('50s - 60s'), {
                self.lookup_kwarg_since: 50000000000,
                self.lookup_kwarg_until: 60000000000,
            }),
            (_('> 60s'), {
                self.lookup_kwarg_since: 60000000000,
                self.lookup_kwarg_until: None,
            }),
        )


class TagCategoryListFilter(RelatedFieldListFilter):

    """ Adds filtering by TagCategory, based on tags on Asset.  If a
    TagCategory is clicked the filter list displays specific tags in that
    TagCategory.
    """
    # Parameter for the filter that will be used in the querystring.
    parameter_name = 'tagcategory'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.field = field
        self.field_path = field_path
        self.used_parameters = {}
        self.lookup_kwarg_isnull = '%s__isnull' % field_path

        other_model = get_model_from_relation(field)
        rel_name = other_model._meta.pk.name

        if "tags__tag_category__name__iexact" in request.GET:
            self.lookup_kwarg = '%s__description' % field_path
            self.lookup_val = request.GET.get(self.lookup_kwarg, None)
            # getting the first char of values
            cat_t = request.GET.get("tags__tag_category__name__iexact")
            cat = TagCategory.objects.get(name__iexact=cat_t)
            tags = Tag.objects.filter(tag_category__id__exact="%s" % cat.pk)
            self.lookup_choices = list(tag.description for tag in tags)
            self.lookup_choices.sort()
        else:
            self.lookup_kwarg = '%s__tag_category__name__iexact' % field_path
            self.lookup_val = request.GET.get(self.lookup_kwarg, None)
            # getting the first char of values
            self.lookup_choices = list(
                cat.name for cat in TagCategory.objects.all())
            self.lookup_choices.sort()

        for p in self.expected_parameters():
            if p in params:
                value = params.pop(p)
                self.used_parameters[p] = prepare_lookup_value(p, value)

        # super(RelatedFieldListFilter, self).__init__(
        #     field, request, params, model, model_admin, field_path)

        self.title = _('tag category')

    def has_output(self):
        return True

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_isnull]

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
               'query_string': "?",
               'display': _('All Categories')}
        yield {'selected': self.lookup_val is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
               'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val) == self.lookup_val,
                   'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                   'display': val}
