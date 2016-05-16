from roundware.rw.models import Event, Asset, ListeningHistoryItem, Tag, TagRelationship, UIItem, UIGroup
from distutils.util import strtobool
import django_filters

BOOLEAN_CHOICES = (('false', False), ('true', True),
                   (0, False), (1, True),)


class IntegerListFilter(django_filters.Filter):
    def filter(self, qs, value):
        if value not in (None, ''):
            integers = [int(v) for v in value.split(',')]
            return qs.filter(**{'%s__%s' % (self.name, self.lookup_type): integers})
        return qs


class WordListFilter(django_filters.Filter):
    def filter(self, qs, value):
        if value not in (None, ''):
            words = [str(v) for v in value.split(',')]
            for word in words:
                qs = qs.filter(**{'%s__%s' % (self.name, self.lookup_type): word})
            return qs
        return qs


class NanoNumberFilter(django_filters.NumberFilter):
    def filter(self, qs, value):
        value = round(value * 1000000000, 2)
        return super(NanoNumberFilter, self).filter(qs, value)


class EventFilterSet(django_filters.FilterSet):
    event_type = django_filters.CharFilter(lookup_type='icontains')
    server_time = django_filters.DateTimeFilter(lookup_type='startswith')
    server_time__lt = django_filters.DateTimeFilter(name='server_time', lookup_type='lt')
    server_time__gt = django_filters.DateTimeFilter(name='server_time', lookup_type='gt')
    session_id = django_filters.NumberFilter()
    latitude = django_filters.CharFilter(lookup_type='startswith')
    longitude = django_filters.CharFilter(lookup_type='startswith')
    tag_ids = WordListFilter(name='tags', lookup_type='contains')

    class Meta:
        model = Event
        fields = ['event_type',
                  'server_time',
                  'session_id',
                  'latitude',
                  'longitude',
                  'tags']


class AssetFilterSet(django_filters.FilterSet):
    session_id = django_filters.NumberFilter()
    project_id = django_filters.NumberFilter()
    tag_ids = IntegerListFilter(name='tags', lookup_type='in')
    media_type = django_filters.CharFilter(name='mediatype')
    language = django_filters.CharFilter(name='language__language_code')
    envelope_id = django_filters.NumberFilter()
    longitude = django_filters.NumberFilter(lookup_type='startswith')
    latitude = django_filters.NumberFilter(lookup_type='startswith')
    submitted = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    audiolength__lte = NanoNumberFilter(name='audiolength', lookup_type='lte')
    audiolength__gte = NanoNumberFilter(name='audiolength', lookup_type='gte')
    created__lte = django_filters.DateTimeFilter(name='created', lookup_type='lte')
    created__gte = django_filters.DateTimeFilter(name='created', lookup_type='gte')

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


class ListeningHistoryItemFilterSet(django_filters.FilterSet):
    duration__lte = django_filters.NumberFilter('duration', lookup_type='lte')
    duration__gte = django_filters.NumberFilter('duration', lookup_type='gte')
    start_time__gte = django_filters.DateTimeFilter(name='starttime', lookup_type='gte')
    start_time__lte = django_filters.DateTimeFilter(name='starttime', lookup_type='lte')
    start_time__range = django_filters.DateRangeFilter(name='starttime')

    class Meta:
        model = ListeningHistoryItem
        fields = ['starttime',
                  'session',
                  'asset',
                  ]


class TagFilterSet(django_filters.FilterSet):
    description = django_filters.CharFilter(lookup_type='icontains')
    data = django_filters.CharFilter(lookup_type='icontains')

    class Meta:
        model = Tag


class TagRelationshipFilterSet(django_filters.FilterSet):
    tag_id = django_filters.NumberFilter()
    parent_id = django_filters.NumberFilter()

    class Meta:
        model = TagRelationship


class UIGroupFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='startswith')
    ui_mode = django_filters.TypedChoiceFilter(choices=UIGroup.UI_MODES)
    tag_category_id = django_filters.NumberFilter()
    select = django_filters.TypedChoiceFilter(choices=UIGroup.SELECT_METHODS)
    active = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    index = django_filters.NumberFilter()
    project_id = django_filters.NumberFilter()

    class Meta:
        model = UIGroup


class UIItemFilterSet(django_filters.FilterSet):
    ui_group_id = django_filters.NumberFilter()
    index = django_filters.NumberFilter()
    tag_id = django_filters.NumberFilter()
    default = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    active = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    parent_id = django_filters.NumberFilter()

    class Meta:
        model = UIItem
