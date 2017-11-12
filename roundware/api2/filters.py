# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from roundware.rw.models import (Asset, Audiotrack, Envelope, Event, Language, ListeningHistoryItem,
                                 LocalizedString, Project, ProjectGroup, Session, Speaker, Tag, TagCategory,
                                 TagRelationship, TimedAsset, UIItem, UIGroup, Vote)
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


class AudiotrackFilterSet(django_filters.FilterSet):
    project_id = django_filters.NumberFilter()
    minduration__lte = NanoNumberFilter(name='minduration', lookup_type='lte')
    minduration__gte = NanoNumberFilter(name='minduration', lookup_type='gte')
    maxduration__lte = NanoNumberFilter(name='maxduration', lookup_type='lte')
    maxduration__gte = NanoNumberFilter(name='maxduration', lookup_type='gte')
    mindeadair__lte = NanoNumberFilter(name='mindeadair', lookup_type='lte')
    mindeadair__gte = NanoNumberFilter(name='mindeadair', lookup_type='gte')
    maxdeadair__lte = NanoNumberFilter(name='maxdeadair', lookup_type='lte')
    maxdeadair__gte = NanoNumberFilter(name='maxdeadair', lookup_type='gte')

    class Meta:
        model = Audiotrack
        fields = ['project_id',
                  'minduration',
                  'maxduration',
                  'mindeadair',
                  'maxdeadair']


class EnvelopeFilterSet(django_filters.FilterSet):
    session_id = django_filters.NumberFilter()
    project_id = django_filters.NumberFilter(name='session__project_id')
    asset_id = django_filters.NumberFilter(name='assets')

    class Meta:
        model = Envelope


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


class LanguageFilterSet(django_filters.FilterSet):
    language_code = django_filters.CharFilter(lookup_type='icontains')
    name = django_filters.CharFilter(lookup_type='icontains')

    class Meta:
        model = Language


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
                  'asset']


class LocalizedStringFilterSet(django_filters.FilterSet):
    language_id = django_filters.NumberFilter()
    language = django_filters.CharFilter(name='language__language_code')
    localized_string = django_filters.CharFilter(lookup_type='icontains')

    class Meta:
        model = LocalizedString


class ProjectFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    listen_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    geo_listen_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    speak_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    geo_speak_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)

    class Meta:
        model = Project


class ProjectGroupFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    active = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)

    class Meta:
        model = ProjectGroup


class SessionFilterSet(django_filters.FilterSet):
    project_id = django_filters.NumberFilter()
    language_id = django_filters.NumberFilter()
    language = django_filters.CharFilter(name='language__language_code')
    geo_listen_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    demo_stream_enabled = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)

    class Meta:
        model = Session


class SpeakerFilterSet(django_filters.FilterSet):
    activeyn = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool)
    project_id = django_filters.NumberFilter()

    class Meta:
        model = Speaker


class TagFilterSet(django_filters.FilterSet):
    description = django_filters.CharFilter(lookup_type='icontains')
    data = django_filters.CharFilter(lookup_type='icontains')
    project_id = django_filters.NumberFilter()

    class Meta:
        model = Tag


class TagCategoryFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')

    class Meta:
        model = TagCategory


class TagRelationshipFilterSet(django_filters.FilterSet):
    tag_id = django_filters.NumberFilter()
    parent_id = django_filters.NumberFilter()

    class Meta:
        model = TagRelationship


class TimedAssetFilterSet(django_filters.FilterSet):
    project_id = django_filters.NumberFilter()
    asset_id = django_filters.NumberFilter()
    start__lte = django_filters.NumberFilter(name='start', lookup_type='lte')
    start__gte = django_filters.NumberFilter(name='start', lookup_type='gte')
    end__lte = django_filters.NumberFilter(name='end', lookup_type='lte')
    end__gte = django_filters.NumberFilter(name='end', lookup_type='gte')

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

class VoteFilterSet(django_filters.FilterSet):
    voter_id = django_filters.NumberFilter()
    session_id = django_filters.NumberFilter()
    asset_id = django_filters.NumberFilter()
    type = django_filters.TypedChoiceFilter(choices=Vote.VOTE_TYPES)
    value = django_filters.NumberFilter()

    class Meta:
        model = Vote
