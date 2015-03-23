from roundware.rw.models import Event, Asset, ListeningHistoryItem, Tag
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
                  'submitted']


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
