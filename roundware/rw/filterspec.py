# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.db import models
from django.contrib.admin.filterspecs import (FilterSpec, ChoicesFilterSpec,
                                             RelatedFilterSpec,
                                             DateFieldFilterSpec)
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from models import TagCategory, Tag


class TagCategoryFilterSpec(RelatedFilterSpec):

    """
    Adds filtering by first char (alphabetic style) of values in the admin
    filter sidebar. Set the alphabetic filter in the model field attribute
    'alphabetic_filter'.

    my_model_field.alphabetic_filter = True
    """

    def __init__(self, f, request, params, model, model_admin, *args, **kwargs):
        super(TagCategoryFilterSpec, self).__init__(
            f, request, params, model, model_admin, *args, **kwargs)

        self.lookup_kwarg = '%s__tag_category__name__iexact' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        # getting the first char of values
        self.lookup_choices = list(
            cat.name for cat in TagCategory.objects.all())
        self.lookup_choices.sort()

        if "tags__tag_category__name__iexact" in request.GET:
            self.lookup_kwarg = '%s__description' % f.name
            self.lookup_val = request.GET.get(self.lookup_kwarg, None)
            # getting the first char of values
            cat_t = request.GET.get("tags__tag_category__name__iexact")
            cat = TagCategory.objects.get(name__iexact=cat_t)
            tags = Tag.objects.filter(tag_category__id__exact="%s" % cat.pk)
            self.lookup_choices = list(tag.description for tag in tags)
            self.lookup_choices.sort()
        else:
            self.lookup_kwarg = '%s__tag_category__name__iexact' % f.name
            self.lookup_val = request.GET.get(self.lookup_kwarg, None)
            # getting the first char of values
            self.lookup_choices = list(
                cat.name for cat in TagCategory.objects.all())
            self.lookup_choices.sort()

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

    def title(self):
        return _('%(field_name)s') %\
            {'field_name': self.field.verbose_name}

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'tag_category_filter', False),
                                   TagCategoryFilterSpec))


class AudioLengthFilterSpec(DateFieldFilterSpec):

    """
    Adds filtering by future and previous values in the admin
    filter sidebar. Set the is_active_filter filter in the model field attribute 'is_active_filter'.

    my_model_field.is_active_filter = True
    """

    def __init__(self, f, request, params, model, model_admin, *args, **kwargs):
        super(AudioLengthFilterSpec, self).__init__(
            f, request, params, model, model_admin, *args, **kwargs)
        self.links = (
            (_('Any'), {}),
            (_('< 10s'), {'%s__lt' % self.field.name: 10000000000, }),
            (_('10s - 20s'), {'%s__gte' % self.field.name: 10000000000,
                              '%s__lt' % self.field.name: 20000000000}),
            (_('20s - 30s'), {'%s__gte' % self.field.name: 20000000000,
                              '%s__lt' % self.field.name: 30000000000}),
            (_('30s - 40s'), {'%s__gte' % self.field.name: 30000000000,
                              '%s__lt' % self.field.name: 40000000000}),
            (_('40s - 50s'), {'%s__gte' % self.field.name: 40000000000,
                              '%s__lt' % self.field.name: 50000000000}),
            (_('50s - 60s'), {'%s__gte' % self.field.name: 50000000000,
                              '%s__lt' % self.field.name: 60000000000}),
            (_('60s +'), {'%s__gte' % self.field.name: 60000000000})
        )

    def title(self):
        return "Audio File Length"

        # Register the filter

FilterSpec.filter_specs.insert(
    0, (lambda f: getattr(f, 'audio_length_filter', False), AudioLengthFilterSpec))
