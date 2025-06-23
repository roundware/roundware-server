import pytest
from model_bakery import baker
from django.utils import timezone
from roundware.api2.filters import (
    AssetFilterSet, IntegerListFilter, IntegerListAndFilter,
    WordListFilter, DescriptionFilenameAssetFilter, NanoNumberFilter,
    UserNameEmailFilter, NameEmailUserFilter
)
from roundware.rw.models import Asset, Tag, Project, Session, Language
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestAssetFilters:
    def test_session_id_filter(self):
        # Create test data
        session = baker.make(Session)
        asset = baker.make(Asset, session=session)
        baker.make(Asset)  # Create another asset with different session

        # Test the filter
        filterset = AssetFilterSet({'session_id': session.id})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == asset

    def test_tag_ids_or_filter(self):
        # Create test data
        tags = baker.make(Tag, _quantity=2)
        asset1 = baker.make(Asset)
        asset1.tags.add(tags[0])
        asset2 = baker.make(Asset)
        asset2.tags.add(tags[1])
        asset3 = baker.make(Asset)  # Asset with no tags

        # Test OR filter with one tag
        filterset = AssetFilterSet({'tag_ids_or': str(tags[0].id)})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == asset1

        # Test OR filter with multiple tags
        filterset = AssetFilterSet({'tag_ids_or': f"{tags[0].id},{tags[1].id}"})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 2
        assert set(filtered_qs) == {asset1, asset2}

    def test_tag_ids_and_filter(self):
        # Create test data
        tags = baker.make(Tag, _quantity=2)
        asset1 = baker.make(Asset)
        asset1.tags.add(tags[0], tags[1])  # Asset with both tags
        asset2 = baker.make(Asset)
        asset2.tags.add(tags[0])  # Asset with only first tag
        asset3 = baker.make(Asset)  # Asset with no tags

        # Test AND filter
        filterset = AssetFilterSet({'tag_ids': f"{tags[0].id},{tags[1].id}"})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == asset1

    def test_description_filename_filter(self):
        # Create test data
        asset1 = baker.make(Asset, description="test description")
        asset2 = baker.make(Asset, filename="test_file.mp3")
        asset3 = baker.make(Asset)  # Asset with no matching text

        # Test description filter
        filterset = AssetFilterSet({'description': 'test'})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == asset1

        # Test filename filter
        filterset = AssetFilterSet({'filename': 'test'})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == asset2

        # Test text_filter (searches both description and filename)
        filterset = AssetFilterSet({'text_filter': 'test'})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 2
        assert set(filtered_qs) == {asset1, asset2}

    def test_date_range_filters(self):
        # Create test data
        now = timezone.now()
        asset1 = baker.make(Asset, created=now - timezone.timedelta(days=1))
        asset2 = baker.make(Asset, created=now)
        asset3 = baker.make(Asset, created=now + timezone.timedelta(days=1))

        # Test created__gte filter
        filterset = AssetFilterSet({'created__gte': now})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 2
        assert set(filtered_qs) == {asset2, asset3}

        # Test created__lte filter
        filterset = AssetFilterSet({'created__lte': now})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 2
        assert set(filtered_qs) == {asset1, asset2}

    def test_nano_number_filter(self):
        # Create test data (audiolength in nanoseconds)
        asset1 = baker.make(Asset, audiolength=1.5 * 1_000_000_000)  # 1.5 seconds
        asset2 = baker.make(Asset, audiolength=2.0 * 1_000_000_000)  # 2.0 seconds
        asset3 = baker.make(Asset, audiolength=2.5 * 1_000_000_000)  # 2.5 seconds

        # Test lte filter (should include 1.5s and 2.0s)
        filterset = AssetFilterSet({'audiolength__lte': 2.0})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 2
        assert set(filtered_qs) == {asset1, asset2}

        # Test gte filter (should include 2.0s and 2.5s)
        filterset = AssetFilterSet({'audiolength__gte': 2.0})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 2
        assert set(filtered_qs) == {asset2, asset3}

    def test_word_list_filter(self):
        # Create test data
        event1 = baker.make('rw.Event', tags=['tag1', 'tag2'])
        event2 = baker.make('rw.Event', tags=['tag2', 'tag3'])
        event3 = baker.make('rw.Event', tags=['tag3', 'tag4'])

        # Test single word filter (should match events with 'tag1')
        filter_instance = WordListFilter(field_name='tags', lookup_expr='contains')
        filtered_qs = filter_instance.filter(type(event1).objects.all(), 'tag1')
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == event1

        # Test multiple words filter (should match only event1, which has both 'tag1' and 'tag2')
        filtered_qs = filter_instance.filter(type(event1).objects.all(), 'tag1,tag2')
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == event1

    def test_word_list_filter_empty_value(self):
        # Should return the original queryset if value is None or ''
        event1 = baker.make('rw.Event', tags=['tag1'])
        qs = type(event1).objects.all()
        filter_instance = WordListFilter(field_name='tags', lookup_expr='contains')
        assert list(filter_instance.filter(qs, None)) == list(qs)
        assert list(filter_instance.filter(qs, '')) == list(qs)

    def test_user_name_email_filter(self):
        # Create test data
        user1 = baker.make(User, username='user1', email='user1@test.com', first_name='John', last_name='Doe')
        user2 = baker.make(User, username='user2', email='user2@test.com', first_name='Jane', last_name='Smith')
        asset1 = baker.make(Asset, user=user1)
        asset2 = baker.make(Asset, user=user2)

        # Test username filter
        filterset = AssetFilterSet({'user_str': 'user1'})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == asset1

        # Test email filter
        filterset = AssetFilterSet({'user_str': 'user1@test.com'})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == asset1

        # Test name filter
        filterset = AssetFilterSet({'user_str': 'John'})
        filtered_qs = filterset.qs
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == asset1

    def test_name_email_user_filter(self):
        # Create test data
        user1 = baker.make(User, username='user1', email='user1@test.com', first_name='John', last_name='Doe')
        user2 = baker.make(User, username='user2', email='user2@test.com', first_name='Jane', last_name='Smith')

        # Test username filter
        filter_instance = NameEmailUserFilter(lookup_expr='icontains')
        filtered_qs = filter_instance.filter(User.objects.all(), 'user1')
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == user1

        # Test email filter
        filtered_qs = filter_instance.filter(User.objects.all(), 'user1@test.com')
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == user1

        # Test name filter
        filtered_qs = filter_instance.filter(User.objects.all(), 'John')
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == user1

    def test_name_email_user_filter_empty_value(self):
        # Should return the original queryset if value is None or ''
        user1 = baker.make(User, username='user1')
        qs = User.objects.all()
        filter_instance = NameEmailUserFilter(lookup_expr='icontains')
        assert list(filter_instance.filter(qs, None)) == list(qs)
        assert list(filter_instance.filter(qs, '')) == list(qs)

@pytest.mark.django_db
class TestIntegerListFilters:
    def test_integer_list_filter(self):
        # Create test data
        project = baker.make(Project)
        assets = baker.make(Asset, _quantity=3, project=project)
        
        # Test the filter
        filter_instance = IntegerListFilter(field_name='id', lookup_expr='in')
        filtered_qs = filter_instance.filter(Asset.objects.all(), f"{assets[0].id},{assets[1].id}")
        assert filtered_qs.count() == 2
        assert set(filtered_qs) == {assets[0], assets[1]}

    def test_integer_list_and_filter(self):
        # Create test data
        tags = baker.make(Tag, _quantity=2)
        asset1 = baker.make(Asset)
        asset1.tags.add(tags[0], tags[1])
        asset2 = baker.make(Asset)
        asset2.tags.add(tags[0])
        
        # Test the filter
        filter_instance = IntegerListAndFilter(field_name='tags__id')
        filtered_qs = filter_instance.filter(Asset.objects.all(), f"{tags[0].id},{tags[1].id}")
        assert filtered_qs.count() == 1
        assert filtered_qs.first() == asset1 