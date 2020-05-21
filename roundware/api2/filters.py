# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.
import numbers

from roundware.rw.models import (Asset, Audiotrack, Envelope, Event, Language, ListeningHistoryItem,
                                 LocalizedString, Project, ProjectGroup, Session, Speaker, Tag, TagCategory,
                                 TagRelationship, TimedAsset, UIElement, UIElementName, UIItem, UIGroup, Vote)
from distutils.util import strtobool
import django_filters
from django.db.models import Q

BOOLEAN_CHOICES = (('false', False), ('true', True),
                   (0, False), (1, True),)


class IntegerListFilter(django_filters.Filter):
    # perform OR filter with list of integers
    def filter(self, qs, value):
        if value not in (None, ''):
            integers = [int(v) for v in value.split(',')]
            return qs.filter(**{'%s__%s' % (self.name, self.lookup_expr): integers})
        return qs

class IntegerListAndFilter(django_filters.Filter):
    # perform AND filter with list of integers
    def filter(self, qs, value):
        if value not in (None, ''):
            integers = [int(v) for v in value.split(',')]
            # loop through each integer in list filtering each time to return only
            # objects that contain ALL integers, not ANY integers;
            # effectively, this creates a chain of .filters
            for i in integers:
                qs = qs.filter(**{'%s' % (self.name): i})
        return qs

class WordListFilter(django_filters.Filter):
    def filter(self, qs, value):
        if value not in (None, ''):
            words = [str(v) for v in value.split(',')]
            for word in words:
                qs = qs.filter(**{'%s__%s' % (self.field_name, self.lookup_expr): word})
            return qs
        return qs

class DescriptionFilenameAssetFilter(django_filters.CharFilter):
  def filter(self, qs, value):
    if value:
      return qs.filter(Q(**{'description__'+ self.lookup_expr: value}) |
                       Q(**{'filename__'+ self.lookup_expr: value}))
    return qs

class NanoNumberFilter(django_filters.NumberFilter):
    def filter(self, qs, value):
        if isinstance(value, numbers.Number):
            value = round(value * 1000000000, 2)
        return super(NanoNumberFilter, self).filter(qs, value)


class UserNameEmailFilter(django_filters.CharFilter):
  def filter(self, qs, value):
    if value:
      return qs.filter(Q(**{'user__first_name__'+ self.lookup_expr: value}) |
                       Q(**{'user__last_name__'+ self.lookup_expr: value}) |
                       Q(**{'user__email__'+ self.lookup_expr: value}) |
                       Q(**{'user__username__'+ self.lookup_expr: value}))
    return qs


class AssetFilterSet(django_filters.FilterSet):
    session_id = django_filters.NumberFilter()
    project_id = django_filters.NumberFilter()
    # TODO: allow param to choose between AND or OR filtering
    tag_ids_or = IntegerListFilter(field_name='tags', lookup_expr='in') # performs OR filtering
    tag_ids = IntegerListAndFilter(field_name='tags__id') # performs AND filtering
    media_type = django_filters.CharFilter(field_name='mediatype')
    language = django_filters.CharFilter(field_name='language__language_code')
    envelope_id = IntegerListAndFilter(field_name='envelope__id')
    longitude = django_filters.NumberFilter(lookup_expr='startswith')
    latitude = django_filters.NumberFilter(lookup_expr='startswith')
    submitted = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    audiolength__lte = NanoNumberFilter(field_name='audiolength', lookup_expr='lte')
    audiolength__gte = NanoNumberFilter(field_name='audiolength', lookup_expr='gte')
    created__lte = django_filters.DateTimeFilter(field_name='created', lookup_expr='lte')
    created__gte = django_filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    updated__lte = django_filters.DateTimeFilter(field_name='updated', lookup_expr='lte')
    updated__gte = django_filters.DateTimeFilter(field_name='updated', lookup_expr='gte')
    description = django_filters.CharFilter(lookup_expr='icontains')
    filename = django_filters.CharFilter(lookup_expr='icontains')
    text_filter = DescriptionFilenameAssetFilter(lookup_expr='icontains')
    user_str = UserNameEmailFilter(lookup_expr='icontains')

    class Meta:
        model = Asset
        fields = ['session',
                  'project',
                  'tags',
                  'mediatype',
                  'language',
                  'envelope',
                  'longitude',
                  'latitude',
                  'submitted',
                  'audiolength',
                  'created']


class AudiotrackFilterSet(django_filters.FilterSet):
    project_id = django_filters.NumberFilter()
    minduration__lte = NanoNumberFilter(field_name='minduration', lookup_expr='lte')
    minduration__gte = NanoNumberFilter(field_name='minduration', lookup_expr='gte')
    maxduration__lte = NanoNumberFilter(field_name='maxduration', lookup_expr='lte')
    maxduration__gte = NanoNumberFilter(field_name='maxduration', lookup_expr='gte')
    mindeadair__lte = NanoNumberFilter(field_name='mindeadair', lookup_expr='lte')
    mindeadair__gte = NanoNumberFilter(field_name='mindeadair', lookup_expr='gte')
    maxdeadair__lte = NanoNumberFilter(field_name='maxdeadair', lookup_expr='lte')
    maxdeadair__gte = NanoNumberFilter(field_name='maxdeadair', lookup_expr='gte')
    active = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    repeatrecordings = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    start_with_silence = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    fadeout_when_filtered = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)

    class Meta:
        model = Audiotrack
        fields = ['project_id',
                  'minduration',
                  'maxduration',
                  'mindeadair',
                  'maxdeadair']


class EnvelopeFilterSet(django_filters.FilterSet):
    session_id = django_filters.NumberFilter()
    project_id = django_filters.NumberFilter(field_name='session__project_id')
    asset_id = django_filters.NumberFilter(field_name='assets')

    class Meta:
        model = Envelope
        exclude = []


class EventFilterSet(django_filters.FilterSet):
    event_type = django_filters.CharFilter(lookup_expr='icontains')
    server_time = django_filters.DateTimeFilter(lookup_expr='startswith')
    server_time__lt = django_filters.DateTimeFilter(field_name='server_time', lookup_expr='lt')
    server_time__gt = django_filters.DateTimeFilter(field_name='server_time', lookup_expr='gt')
    session_id = django_filters.NumberFilter()
    latitude = django_filters.CharFilter(lookup_expr='startswith')
    longitude = django_filters.CharFilter(lookup_expr='startswith')
    tag_ids = WordListFilter(field_name='tags', lookup_expr='contains')

    class Meta:
        model = Event
        fields = ['event_type',
                  'server_time',
                  'session_id',
                  'latitude',
                  'longitude',
                  'tags']


class LanguageFilterSet(django_filters.FilterSet):
    language_code = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Language
        exclude = []



class ListeningHistoryItemFilterSet(django_filters.FilterSet):
    duration__lte = django_filters.NumberFilter('duration', lookup_expr='lte')
    duration__gte = django_filters.NumberFilter('duration', lookup_expr='gte')
    start_time__gte = django_filters.DateTimeFilter(field_name='starttime', lookup_expr='gte')
    start_time__lte = django_filters.DateTimeFilter(field_name='starttime', lookup_expr='lte')
    start_time__range = django_filters.DateRangeFilter(field_name='starttime')

    class Meta:
        model = ListeningHistoryItem
        fields = ['starttime',
                  'session',
                  'asset']


class LocalizedStringFilterSet(django_filters.FilterSet):
    language_id = django_filters.NumberFilter()
    language = django_filters.CharFilter(field_name='language__language_code')
    localized_string = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = LocalizedString
        exclude = []


class ProjectFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    listen_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    geo_listen_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    speak_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    geo_speak_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)

    class Meta:
        model = Project
        exclude = []


class ProjectGroupFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    active = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)

    class Meta:
        model = ProjectGroup
        exclude = []


class SessionFilterSet(django_filters.FilterSet):
    project_id = django_filters.NumberFilter()
    language_id = django_filters.NumberFilter()
    language = django_filters.CharFilter(field_name='language__language_code')
    geo_listen_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    demo_stream_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)

    class Meta:
        model = Session
        exclude = []


class SpeakerFilterSet(django_filters.FilterSet):
    activeyn = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    project_id = django_filters.NumberFilter()

    class Meta:
        model = Speaker
        fields = ["activeyn", "project_id"]


class TagFilterSet(django_filters.FilterSet):
    description = django_filters.CharFilter(lookup_expr='icontains')
    data = django_filters.CharFilter(lookup_expr='icontains')
    project_id = django_filters.NumberFilter()

    class Meta:
        model = Tag
        fields = ['description', 'data', 'project_id']

class TagCategoryFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = TagCategory
        exclude = []


class TagRelationshipFilterSet(django_filters.FilterSet):
    tag_id = django_filters.NumberFilter()
    parent_id = django_filters.NumberFilter()

    class Meta:
        model = TagRelationship
        exclude = []


class TimedAssetFilterSet(django_filters.FilterSet):
    project_id = django_filters.NumberFilter()
    asset_id = django_filters.NumberFilter()
    start__lte = django_filters.NumberFilter(field_name='start', lookup_expr='lte')
    start__gte = django_filters.NumberFilter(field_name='start', lookup_expr='gte')
    end__lte = django_filters.NumberFilter(field_name='end', lookup_expr='lte')
    end__gte = django_filters.NumberFilter(field_name='end', lookup_expr='gte')

    class Meta:
        model = TimedAsset
        fields = ['project_id',
                  'asset_id',
                  'start',
                  'end']


class UIConfigFilterSet(django_filters.FilterSet):
    project_id = django_filters.NumberFilter()
    ui_mode = django_filters.TypedChoiceFilter(choices=UIGroup.UI_MODES)
    active = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)

    class Meta:
        model = UIGroup
        exclude = []


class UIElementFilterSet(django_filters.FilterSet):
    uielementname = django_filters.CharFilter(field_name='uielementname__name', lookup_expr='contains')
    project_id = django_filters.NumberFilter()
    variant = django_filters.TypedChoiceFilter(choices=UIElement.VARIANTS)
    file_extension = django_filters.TypedChoiceFilter(choices=UIElement.FILE_EXTENSIONS)

    class Meta:
        model = UIElement
        exclude = []


class UIElementNameFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='contains')
    view = django_filters.TypedChoiceFilter(choices=UIElementName.VIEWS)

    class Meta:
        model = UIElementName
        exclude = []


class UIGroupFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='startswith')
    ui_mode = django_filters.TypedChoiceFilter(choices=UIGroup.UI_MODES)
    tag_category_id = django_filters.NumberFilter()
    select = django_filters.TypedChoiceFilter(choices=UIGroup.SELECT_METHODS)
    active = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    index = django_filters.NumberFilter()
    project_id = django_filters.NumberFilter()

    class Meta:
        model = UIGroup
        exclude = []


class UIItemFilterSet(django_filters.FilterSet):
    ui_group_id = django_filters.NumberFilter()
    index = django_filters.NumberFilter()
    tag_id = django_filters.NumberFilter()
    default = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    active = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    parent_id = django_filters.NumberFilter()
    project_id = django_filters.NumberFilter(field_name='ui_group_id__project_id')

    class Meta:
        model = UIItem
        exclude = []


class VoteFilterSet(django_filters.FilterSet):
    voter_id = django_filters.NumberFilter()
    session_id = django_filters.NumberFilter()
    project_id = django_filters.NumberFilter(field_name='session_id__project_id')
    asset_id = django_filters.NumberFilter()
    type = django_filters.TypedChoiceFilter(choices=Vote.VOTE_TYPES)
    value = django_filters.NumberFilter()
    media_type = django_filters.CharFilter(field_name='asset_id__mediatype')

    class Meta:
        model = Vote
        exclude = []
