from roundware.rw.models import Event
import django_filters


class EventFilter(django_filters.FilterSet):
    event_type = django_filters.CharFilter(lookup_type='startswith')
    server_time = django_filters.DateTimeFilter(lookup_type='startswith')
    server_time__lt = django_filters.DateTimeFilter(name='server_time', lookup_type='lt')
    server_time__gt = django_filters.DateTimeFilter(name='server_time', lookup_type='gt')
    session_id = django_filters.NumberFilter()
    latitude = django_filters.NumberFilter()
    longitude = django_filters.NumberFilter()
    tags = django_filters.CharFilter(lookup_type='icontains')

    class Meta:
        model = Event
        fields = ['event_type',
                  'server_time',
                  'session_id',
                  'latitude',
                  'longitude',
                  'tags']
