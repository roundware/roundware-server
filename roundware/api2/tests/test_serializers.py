import pytest
from model_bakery import baker
from roundware.api2 import serializers
from roundware.rw import models
from django.contrib.auth.models import User
from rest_framework.serializers import ValidationError
from django.conf import settings

@pytest.mark.django_db
def test_admin_locale_string_serializer_get_fields():
    class DummySerializer(serializers.AdminLocaleStringSerializerMixin):
        class Meta:
            localized_fields = ['loc_description']
    s = DummySerializer(context={'admin': True})
    fields = s.get_fields()
    assert 'loc_description_admin' in fields

@pytest.mark.django_db
def test_asset_serializer_to_representation():
    asset = baker.make(models.Asset)
    serializer = serializers.AssetSerializer(asset)
    data = serializer.data
    assert 'media_type' in data
    assert 'audio_length_in_seconds' in data

@pytest.mark.django_db
def test_audiotrack_serializer_to_representation():
    audiotrack = baker.make(models.Audiotrack, minduration=2e9, maxduration=3e9, mindeadair=1e9, maxdeadair=2e9, minfadeintime=1e9, maxfadeintime=2e9, minfadeouttime=1e9, maxfadeouttime=2e9, minpanduration=1e9, maxpanduration=2e9)
    serializer = serializers.AudiotrackSerializer(audiotrack)
    data = serializer.data
    assert data['minduration'] == 2.0
    assert 'project_id' in data

@pytest.mark.django_db
def test_envelope_serializer_validate_and_create():
    session = baker.make(models.Session)
    data = {'session_id': session.id}
    serializer = serializers.EnvelopeSerializer(data=data, context={})
    assert serializer.is_valid()
    envelope = serializer.save()
    assert envelope.session == session

@pytest.mark.django_db
def test_envelope_serializer_to_representation():
    session = baker.make(models.Session)
    envelope = baker.make(models.Envelope, session=session)
    serializer = serializers.EnvelopeSerializer(envelope)
    data = serializer.data
    assert 'asset_ids' in data

@pytest.mark.django_db
def test_event_serializer_to_representation():
    event = baker.make(models.Event, tags='1,2,3', latitude='10.0', longitude='20.0')
    serializer = serializers.EventSerializer(event)
    data = serializer.data
    assert 'session_id' in data
    assert isinstance(data['tag_ids'], list)
    assert isinstance(data['latitude'], float)
    assert isinstance(data['longitude'], float)

@pytest.mark.django_db
def test_language_serializer_validate_language_code():
    baker.make(models.Language, language_code='en')
    serializer = serializers.LanguageSerializer(data={'language_code': 'fr', 'name': 'French'})
    assert serializer.is_valid()
    serializer = serializers.LanguageSerializer(data={'language_code': 'eng', 'name': 'French'})
    assert not serializer.is_valid()
    serializer = serializers.LanguageSerializer(data={'language_code': 'en', 'name': 'English'})
    assert not serializer.is_valid()

@pytest.mark.django_db
def test_listen_event_serializer_to_representation():
    session = baker.make(models.Session)
    asset = baker.make(models.Asset)
    item = baker.make(models.ListeningHistoryItem, session=session, asset=asset)
    serializer = serializers.ListenEventSerializer(item)
    data = serializer.data
    assert 'start_time' in data
    assert 'session_id' in data
    assert 'asset_id' in data
    assert 'project_id' in data

@pytest.mark.django_db
def test_localized_string_serializer_to_representation():
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang)
    serializer = serializers.LocalizedStringSerializer(loc)
    data = serializer.data
    assert 'text' in data
    assert 'language_id' in data
    assert 'language' in data

@pytest.mark.django_db
def test_project_serializer_to_representation():
    baker.make(models.Language, language_code='en')
    project = baker.make(models.Project)
    serializer = serializers.ProjectSerializer(project, context={})
    data = serializer.data
    assert 'language_ids' in data

@pytest.mark.django_db
def test_project_chooser_serializer_to_representation():
    baker.make(models.Language, language_code='en')
    project = baker.make(models.Project)
    serializer = serializers.ProjectChooserSerializer(project, context={'language_code': 'en'})
    data = serializer.data
    assert 'project_id' in data
    assert 'description_loc' in data
    assert 'thumbnail_url' in data

@pytest.mark.django_db
def test_project_group_serializer_to_representation():
    group = baker.make(models.ProjectGroup)
    serializer = serializers.ProjectGroupSerializer(group)
    data = serializer.data
    assert 'project_ids' in data

@pytest.mark.django_db
def test_session_serializer_validate_and_to_representation():
    lang = baker.make(models.Language)
    project = baker.make(models.Project)
    session = baker.make(models.Session, project=project, language=lang, timezone='+0200')
    serializer = serializers.SessionSerializer(session)
    data = serializer.data
    assert 'project_id' in data
    assert 'language_id' in data
    # Test validation
    serializer = serializers.SessionSerializer(data={'language': lang.id, 'timezone': '+0200', 'project': project.id, 'starttime': '2020-01-01T00:00:00Z'})
    assert serializer.is_valid()

@pytest.mark.django_db
def test_speaker_serializer_get_children_and_to_representation():
    project = baker.make(models.Project)
    parent = baker.make(models.Speaker, project=project)
    child = baker.make(models.Speaker, project=project)
    parent.children.add(child)
    serializer = serializers.SpeakerSerializer(parent)
    data = serializer.data
    assert 'children' in data
    assert 'project_id' in data

@pytest.mark.django_db
def test_tag_serializer_to_representation():
    project = baker.make(models.Project)
    category = baker.make(models.TagCategory)
    lang = baker.make(models.Language, language_code='en')
    tag = baker.make(models.Tag, project=project, tag_category=category, value='Test')
    serializer = serializers.TagSerializer(tag, context={'session': None})
    data = serializer.data
    assert 'project_id' in data
    assert 'tag_category_id' in data
    assert 'description_loc' in data
    assert 'msg_loc' in data
    assert 'relationships' in data

@pytest.mark.django_db
def test_tag_category_serializer_to_representation():
    category = baker.make(models.TagCategory)
    serializer = serializers.TagCategorySerializer(category)
    data = serializer.data
    assert 'id' in data

@pytest.mark.django_db
def test_tag_relationship_serializer_to_representation():
    category = baker.make(models.TagCategory)
    parent_tag = baker.make(models.Tag, tag_category=category, value='Parent')
    child_tag = baker.make(models.Tag, tag_category=category, value='Child')
    parent_rel = baker.make(models.TagRelationship, tag=parent_tag, parent=None)
    child_rel = baker.make(models.TagRelationship, tag=child_tag, parent=parent_rel)
    serializer = serializers.TagRelationshipSerializer(child_rel)
    data = serializer.data
    assert 'tag_id' in data
    assert 'parent_id' in data

@pytest.mark.django_db
def test_timed_asset_serializer_validate_and_to_representation():
    project = baker.make(models.Project)
    asset = baker.make(models.Asset)
    timed = baker.make(models.TimedAsset, project=project, asset=asset, start=1.0, end=2.0)
    serializer = serializers.TimedAssetSerializer(timed)
    data = serializer.data
    assert 'asset_id' in data
    assert 'project_id' in data
    # Test validation
    serializer = serializers.TimedAssetSerializer(data={'project': project.id, 'asset': asset.id, 'start': 1.0, 'end': 2.0})
    assert serializer.is_valid()
    serializer = serializers.TimedAssetSerializer(data={'project': project.id, 'asset': asset.id, 'start': 2.0, 'end': 1.0})
    assert not serializer.is_valid()

@pytest.mark.django_db
def test_uiconfig_serializer_to_representation():
    baker.make(models.Language, language_code='en')
    group = baker.make(models.UIGroup)
    serializer = serializers.UIConfigSerializer(group, context={'mode': 'listen'})
    data = serializer.data
    assert 'display_items' in data

@pytest.mark.django_db
def test_uiconfig_item_serializer_to_representation():
    # Ensure only one Language with code 'en' exists
    models.Language.objects.filter(language_code='en').delete()
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang)
    tag = baker.make(models.Tag)
    tag.loc_msg.set([loc])
    tag.save()
    item = baker.make(models.UIItem, tag=tag)
    serializer = serializers.UIConfigItemSerializer(item, context={'mode': 'listen'})
    data = serializer.data
    assert 'tag_id' in data
    assert 'parent_id' in data
    assert 'default_state' in data
    assert 'tag_display_text' in data

@pytest.mark.django_db
def test_uielement_serializer_to_representation():
    element = baker.make(models.UIElement)
    serializer = serializers.UIElementSerializer(element)
    data = serializer.data
    assert 'label_text_loc_ids' in data
    assert 'uielementname_id' in data
    assert 'project_id' in data

@pytest.mark.django_db
def test_uielement_name_serializer_to_representation():
    name = baker.make(models.UIElementName)
    serializer = serializers.UIElementNameSerializer(name)
    data = serializer.data
    assert 'id' in data

@pytest.mark.django_db
def test_uigroup_serializer_to_representation():
    baker.make(models.Language, language_code='en')
    group = baker.make(models.UIGroup)
    serializer = serializers.UIGroupSerializer(group, context={})
    data = serializer.data
    assert 'tag_category_id' in data
    assert 'project_id' in data
    assert 'ui_items' in data

@pytest.mark.django_db
def test_uiitem_serializer_to_representation():
    item = baker.make(models.UIItem)
    serializer = serializers.UIItemSerializer(item)
    data = serializer.data
    assert 'ui_group_id' in data
    assert 'tag_id' in data
    assert 'parent_id' in data

@pytest.mark.django_db
def test_user_serializer_validate_and_create():
    valid_data = {'device_id': 'test-device-123', 'client_type': 'test-client', 'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
    serializer = serializers.UserSerializer(data=valid_data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.username is not None
    assert user.userprofile.device_id == 'test-device-123'
    assert user.userprofile.client_type == 'test-client'
    invalid_data = {'first_name': 'Test', 'last_name': 'User'}
    serializer = serializers.UserSerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert 'non_field_errors' in serializer.errors

@pytest.mark.django_db
def test_user_info_serializer_to_representation():
    user = baker.make(User)
    serializer = serializers.UserInfoSerializer(user)
    data = serializer.data
    assert 'id' in data
    assert 'device_id' in data
    assert 'client_type' in data

@pytest.mark.django_db
def test_vote_serializer_to_representation():
    vote = baker.make(models.Vote)
    serializer = serializers.VoteSerializer(vote)
    data = serializer.data
    assert 'voter_id' in data
    assert 'asset_id' in data
    assert 'session_id' in data
    assert 'asset_votes' in data

@pytest.mark.django_db
def test_vote_summary_serializer_to_representation():
    vote = baker.make(models.Vote)
    serializer = serializers.VoteSummarySerializer(vote, context={'type': 'like'})
    data = serializer.data
    assert 'asset_id' in data
    assert 'asset_votes' in data

# Utility function tests
@pytest.mark.django_db
def test__select_localized_string():
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang)
    result = serializers._select_localized_string([loc.id], session=None)
    assert result == loc.localized_string

@pytest.mark.django_db
def test__select_localized_string_with_code():
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang)
    result = serializers._select_localized_string_with_code([loc.id], language_code='en')
    assert result == loc.localized_string

@pytest.mark.django_db
def test_uielement_project_serializer_to_representation():
    # Create required objects
    language = baker.make(models.Language, language_code="en")
    loc = baker.make(models.LocalizedString, language=language, localized_string="Test Label")
    uien = baker.make(models.UIElementName, name="test_element")
    
    # Create UIElement with required fields
    element = baker.make(models.UIElement,
        uielementname=uien,
        variant="_variant",
        file_extension="png"
    )
    element.label_text_loc.add(loc)
    element.save()
    
    # Create serializer with context
    serializer = serializers.UIElementProjectSerializer(element, context={"lc": "en"})
    result = serializer.to_representation(element)
    
    # Verify the result structure
    assert "test_element" in result
    element_data = result["test_element"]
    assert element_data["file_name"] == "test_element_variant.png"
    assert element_data["label_text"] == "Test Label"
    assert "uielementname" not in element_data
    assert "label_text_loc" not in element_data

@pytest.mark.django_db
def test_envelope_serializer_validate_session_id_error():
    data = {'session_id': 99999}  # Non-existent session ID
    serializer = serializers.EnvelopeSerializer(data=data, context={})
    assert not serializer.is_valid()
    assert 'session_id' in serializer.errors

@pytest.mark.django_db
def test_session_serializer_validate_language_error():
    data = {'language': 99999, 'timezone': '+0200', 'project': 1}  # Non-existent language
    serializer = serializers.SessionSerializer(data=data)
    assert not serializer.is_valid()
    assert 'language' in serializer.errors

@pytest.mark.django_db
def test_session_serializer_validate_timezone_error():
    data = {'language': 1, 'timezone': 'invalid', 'project': 1}  # Invalid timezone format
    serializer = serializers.SessionSerializer(data=data)
    assert not serializer.is_valid()
    assert 'timezone' in serializer.errors

@pytest.mark.django_db
def test_select_localized_string_with_session_language():
    # Test with session language
    session = baker.make(models.Session)
    lang = baker.make(models.Language, language_code='fr')
    session.language = lang
    session.save()
    loc = baker.make(models.LocalizedString, language=lang, localized_string="French Text")
    result = serializers._select_localized_string([loc.id], session=session)
    assert result == "French Text"

@pytest.mark.django_db
def test_select_localized_string_with_code_fallback():
    # Test fallback to English when specified language not found
    models.Language.objects.filter(language_code='en').delete()  # Ensure only one English language exists
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang, localized_string="English Text")
    result = serializers._select_localized_string_with_code([loc.id], language_code='fr')
    assert result == "English Text"

@pytest.mark.django_db
def test_asset_serializer_to_representation_without_user():
    # Test when user doesn't exist
    user = baker.make(User)
    asset = baker.make(models.Asset, user=user)
    user.delete()  # Delete the user after creating the asset
    serializer = serializers.AssetSerializer(asset)
    data = serializer.data
    assert data['user'] is None

@pytest.mark.django_db
def test_project_serializer_to_representation_with_session():
    # Test with session context
    baker.make(models.Language, language_code='en')
    session = baker.make(models.Session)
    project = baker.make(models.Project)
    serializer = serializers.ProjectSerializer(project, context={'session': session})
    data = serializer.data
    assert 'language_ids' in data

@pytest.mark.django_db
def test_uiconfig_serializer_to_representation_without_session():
    # Test without session context
    baker.make(models.Language, language_code='en')
    group = baker.make(models.UIGroup)
    serializer = serializers.UIConfigSerializer(group, context={'mode': 'listen'})
    data = serializer.data
    assert 'display_items' in data

@pytest.mark.django_db
def test_tag_serializer_to_representation_with_session():
    # Test with session context
    baker.make(models.Language, language_code='en')
    session = baker.make(models.Session)
    project = baker.make(models.Project)
    category = baker.make(models.TagCategory)
    tag = baker.make(models.Tag, project=project, tag_category=category)
    serializer = serializers.TagSerializer(tag, context={'session': session})
    data = serializer.data
    assert 'project_id' in data
    assert 'tag_category_id' in data

@pytest.mark.django_db
def test_asset_serializer_to_representation_user_does_not_exist():
    # Covers lines 106-107: User.DoesNotExist
    user = baker.make(User)
    asset = baker.make(models.Asset, user=user)
    user.delete()
    serializer = serializers.AssetSerializer(asset)
    data = serializer.data
    assert data['user'] is None

@pytest.mark.django_db
def test_event_serializer_to_representation_no_tags():
    event = baker.make(models.Event, tags='', latitude=None, longitude=None)
    serializer = serializers.EventSerializer(event)
    data = serializer.data
    assert 'tag_ids' not in data or data['tag_ids'] == []
    assert 'latitude' not in data or data['latitude'] is None
    assert 'longitude' not in data or data['longitude'] is None

@pytest.mark.django_db
def test_language_serializer_to_representation():
    lang = baker.make(models.Language, language_code='es')
    serializer = serializers.LanguageSerializer(lang)
    data = serializer.data
    assert data['language_code'] == 'es'

@pytest.mark.django_db
def test_project_chooser_serializer_to_representation_no_description_loc():
    baker.make(models.Language, language_code='en')
    project = baker.make(models.Project, description_loc=[])
    serializer = serializers.ProjectChooserSerializer(project, context={'language_code': 'en'})
    data = serializer.data
    assert data['description_loc'] == ''

@pytest.mark.django_db
def test_project_chooser_serializer_to_representation_language_fallback():
    # No language_code in context, should fallback to 'en'
    baker.make(models.Language, language_code='en')
    project = baker.make(models.Project)
    serializer = serializers.ProjectChooserSerializer(project, context={})
    data = serializer.data
    assert 'description_loc' in data

@pytest.mark.django_db
def test_tag_serializer_to_representation_no_relationships():
    project = baker.make(models.Project)
    category = baker.make(models.TagCategory)
    lang = baker.make(models.Language, language_code='en')
    tag = baker.make(models.Tag, project=project, tag_category=category, value='Test')
    # No TagRelationship for this tag
    serializer = serializers.TagSerializer(tag, context={'session': None})
    data = serializer.data
    assert data['relationships'] == []

@pytest.mark.django_db
def test_uiconfig_serializer_to_representation_no_uiitems():
    baker.make(models.Language, language_code='en')
    group = baker.make(models.UIGroup)
    # No UIItems for this group
    serializer = serializers.UIConfigSerializer(group, context={'mode': 'listen'})
    data = serializer.data
    assert data['display_items'] == []

@pytest.mark.django_db
def test_uiconfig_item_serializer_to_representation_no_tag():
    # UIItem with no tag (simulate by deleting tag after creation)
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang)
    tag = baker.make(models.Tag)
    item = baker.make(models.UIItem, tag=tag)
    tag_id = tag.id
    tag.delete()
    serializer = serializers.UIConfigItemSerializer(item, context={'mode': 'listen'})
    data = serializer.data
    assert data['tag_display_text'] is None

@pytest.mark.django_db
def test_user_serializer_validate_missing_fields():
    # Missing both device_id and client_type
    serializer = serializers.UserSerializer(data={'username': 'test'})
    assert not serializer.is_valid()
    assert 'non_field_errors' in serializer.errors

@pytest.mark.django_db
def test__select_localized_string_no_match():
    # No matching localized string for language
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang, localized_string='English')
    other_lang = baker.make(models.Language, language_code='fr')
    session = baker.make(models.Session, language=other_lang)
    result = serializers._select_localized_string([loc.id], session=session)
    assert result is None

@pytest.mark.django_db
def test__select_localized_string_with_code_no_match():
    # No matching localized string for language code, should fallback to English
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang, localized_string='English')
    result = serializers._select_localized_string_with_code([loc.id], language_code='fr')
    assert result == 'English'

@pytest.mark.django_db
def test_project_chooser_serializer_to_representation_no_matching_localized_string():
    # description_loc is not empty, but no LocalizedString matches the language
    lang_en = baker.make(models.Language, language_code='en')
    lang_fr = baker.make(models.Language, language_code='fr')
    loc = baker.make(models.LocalizedString, language=lang_en, localized_string='English Desc')
    project = baker.make(models.Project)
    project.description_loc.set([loc])
    project.save()
    
    # Test with French language (should fallback to English string)
    serializer = serializers.ProjectChooserSerializer(project, context={'language_code': 'fr'})
    data = serializer.data
    if isinstance(data['description_loc'], str):
        assert data['description_loc'] == 'English Desc'
    else:
        assert isinstance(data['description_loc'], list)
        assert len(data['description_loc']) == 1
        assert data['description_loc'][0] == loc.id
    
    # Test with English language (should match directly)
    serializer = serializers.ProjectChooserSerializer(project, context={'language_code': 'en'})
    data = serializer.data
    if isinstance(data['description_loc'], str):
        assert data['description_loc'] == 'English Desc'
    else:
        assert isinstance(data['description_loc'], list)
        assert len(data['description_loc']) == 1
        assert data['description_loc'][0] == loc.id

@pytest.mark.django_db
def test_tag_serializer_to_representation_with_relationships():
    project = baker.make(models.Project)
    category = baker.make(models.TagCategory)
    lang = baker.make(models.Language, language_code='en')
    tag = baker.make(models.Tag, project=project, tag_category=category, value='Test')
    parent_tag = baker.make(models.Tag, project=project, tag_category=category, value='Parent')
    parent_rel = baker.make(models.TagRelationship, tag=parent_tag, parent=None)
    child_rel = baker.make(models.TagRelationship, tag=tag, parent=parent_rel)
    serializer = serializers.TagSerializer(tag, context={'session': None})
    data = serializer.data
    assert isinstance(data['relationships'], list)
    assert any('tag_id' in rel for rel in data['relationships'])

@pytest.mark.django_db
def test_uiconfig_serializer_to_representation_exclude_items():
    # Test listen mode with duplicate tag_ids
    lang = baker.make(models.Language, language_code='en')
    group = baker.make(models.UIGroup)
    tag = baker.make(models.Tag)
    loc = baker.make(models.LocalizedString, language=lang, localized_string='Test Message')
    tag.loc_msg.set([loc])
    tag.save()
    item1 = baker.make(models.UIItem, ui_group=group, tag=tag, active=True)
    item2 = baker.make(models.UIItem, ui_group=group, tag=tag, active=True)
    serializer = serializers.UIConfigSerializer(group, context={'mode': 'listen'})
    data = serializer.data
    # Only one item per tag_id should be present
    assert len(data['display_items']) == 1

@pytest.mark.django_db
def test_uielement_serializer_to_representation_label_text_loc():
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang)
    name = baker.make(models.UIElementName)
    project = baker.make(models.Project)
    element = baker.make(models.UIElement, uielementname=name, project=project)
    element.label_text_loc.add(loc)
    element.save()
    serializer = serializers.UIElementSerializer(element)
    data = serializer.data
    assert 'label_text_loc_ids' in data

@pytest.mark.django_db
def test_user_serializer_validate_only_device_id():
    # Only device_id provided, should fail
    serializer = serializers.UserSerializer(data={'device_id': 'abc'})
    assert not serializer.is_valid()
    assert 'non_field_errors' in serializer.errors

@pytest.mark.django_db
def test__select_localized_string_no_ids():
    # loc_str_ids is empty, but Language 'en' exists
    baker.make(models.Language, language_code='en')
    result = serializers._select_localized_string([], session=None)
    assert result is None

@pytest.mark.django_db
def test__select_localized_string_with_code_no_ids():
    # loc_str_ids is empty, but Language 'en' exists
    baker.make(models.Language, language_code='en')
    result = serializers._select_localized_string_with_code([], language_code='en')
    assert result is None

@pytest.mark.django_db
def test_asset_serializer_to_representation_user_does_not_exist_exception():
    # Covers lines 106-107: User.DoesNotExist
    user = baker.make(User)
    asset = baker.make(models.Asset, user=user)
    user.delete()
    serializer = serializers.AssetSerializer(asset)
    data = serializer.data
    assert data['user'] is None

@pytest.mark.django_db
def test_session_serializer_validate_language_missing():
    # Covers lines 325-326: Language.DoesNotExist
    serializer = serializers.SessionSerializer(data={'language': 99999, 'timezone': '+0200', 'project': 1})
    assert not serializer.is_valid()
    assert 'language' in serializer.errors

@pytest.mark.django_db
def test_session_serializer_validate_timezone_invalid():
    # Covers line 332: invalid timezone
    lang = baker.make(models.Language)
    project = baker.make(models.Project)
    serializer = serializers.SessionSerializer(data={'language': lang.id, 'timezone': 'bad', 'project': project.id})
    assert not serializer.is_valid()
    assert 'timezone' in serializer.errors

@pytest.mark.django_db
def test_tag_serializer_to_representation_with_and_without_relationships():
    # Covers 420-425: relationships and field renaming
    project = baker.make(models.Project)
    category = baker.make(models.TagCategory)
    lang = baker.make(models.Language, language_code='en')
    tag = baker.make(models.Tag, project=project, tag_category=category, value='Test')
    # No relationships
    serializer = serializers.TagSerializer(tag, context={'session': None})
    data = serializer.data
    assert data['relationships'] == []
    # With relationships
    parent_tag = baker.make(models.Tag, project=project, tag_category=category, value='Parent')
    parent_rel = baker.make(models.TagRelationship, tag=parent_tag, parent=None)
    child_rel = baker.make(models.TagRelationship, tag=tag, parent=parent_rel)
    serializer = serializers.TagSerializer(tag, context={'session': None})
    data = serializer.data
    assert any('tag_id' in rel for rel in data['relationships'])

@pytest.mark.django_db
def test_uiconfig_serializer_to_representation_listen_mode_duplicate_tags():
    # Covers 505, 517-528: listen mode filtering and del id
    lang = baker.make(models.Language, language_code='en')
    group = baker.make(models.UIGroup)
    tag = baker.make(models.Tag)
    loc = baker.make(models.LocalizedString, language=lang, localized_string='Test Message')
    tag.loc_msg.set([loc])
    tag.save()
    item1 = baker.make(models.UIItem, ui_group=group, tag=tag, active=True)
    item2 = baker.make(models.UIItem, ui_group=group, tag=tag, active=True)
    serializer = serializers.UIConfigSerializer(group, context={'mode': 'listen'})
    data = serializer.data
    assert len(data['display_items']) == 1

@pytest.mark.django_db
def test_uiconfig_item_serializer_to_representation_listen_mode():
    # Covers 559-562: listen mode parent_id set to None
    lang = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang)
    tag = baker.make(models.Tag)
    tag.loc_msg.set([loc])
    tag.save()
    item = baker.make(models.UIItem, tag=tag)
    serializer = serializers.UIConfigItemSerializer(item, context={'mode': 'listen'})
    data = serializer.data
    assert data['parent_id'] is None

@pytest.mark.django_db
def test_uigroup_serializer_to_representation_header_text_loc():
    # Covers 627: for loop for header_text_loc
    baker.make(models.Language, language_code='en')
    group = baker.make(models.UIGroup)
    serializer = serializers.UIGroupSerializer(group, context={})
    data = serializer.data
    assert 'ui_items' in data

@pytest.mark.django_db
def test_user_serializer_create_optional_fields():
    # Covers 683, 687, 691: create with/without optional fields
    data = {'device_id': 'dev123_1', 'client_type': 'ct'}
    serializer = serializers.UserSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.username is not None
    # With all optional fields
    data = {'device_id': 'dev123_2', 'client_type': 'ct', 'first_name': 'A', 'last_name': 'B', 'email': 'a@b.com'}
    serializer = serializers.UserSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.first_name == 'A'
    assert user.last_name == 'B'
    assert user.email == 'a@b.com'
    # Ensure username is unique
    data = {'device_id': 'dev123_3', 'client_type': 'ct', 'first_name': 'C', 'last_name': 'D', 'email': 'c@d.com'}
    serializer = serializers.UserSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.first_name == 'C'
    assert user.last_name == 'D'
    assert user.email == 'c@d.com'
    # Use timestamp for unique username
    data = {'device_id': 'dev123_4', 'client_type': 'ct', 'first_name': 'E', 'last_name': 'F', 'email': 'e@f.com'}
    serializer = serializers.UserSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.first_name == 'E'
    assert user.last_name == 'F'
    assert user.email == 'e@f.com'

@pytest.mark.django_db
def test_vote_summary_serializer_to_representation_context():
    # Covers 740-742: context handling
    vote = baker.make(models.Vote)
    serializer = serializers.VoteSummarySerializer(vote, context={'type': 'like'})
    data = serializer.data
    assert 'asset_votes' in data
    # Without context
    serializer = serializers.VoteSummarySerializer(vote)
    data = serializer.data
    assert 'asset_votes' in data

@pytest.mark.django_db
def test__select_localized_string_with_code_fallback_and_return():
    # Covers 776, 779-777: fallback and return None
    lang_en = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString, language=lang_en, localized_string='English')
    # Fallback to English
    result = serializers._select_localized_string_with_code([loc.id], language_code='fr')
    assert result == 'English'
    # Return None if no match
    result = serializers._select_localized_string_with_code([], language_code='en')
    assert result is None

@pytest.mark.django_db
def test_asset_serializer_with_all_fields():
    user = baker.make(User)
    project = baker.make(models.Project)
    session = baker.make(models.Session)
    envelope = baker.make(models.Envelope, session=session)
    language = baker.make(models.Language)
    asset = baker.make(models.Asset,
        user=user,
        project=project,
        session=session,
        envelope=[envelope],
        language=language,
        mediatype='audio',
        audiolength=10000000000,  # 10 seconds in nanoseconds
        volume=1.0,
        weight=1.0,
        latitude=10.0,
        longitude=20.0,
        shape='MULTIPOLYGON(((20.0 10.0, 20.1 10.0, 20.1 10.1, 20.0 10.1, 20.0 10.0)))'  # WKT format for a small square polygon
    )
    
    serializer = serializers.AssetSerializer(asset)
    data = serializer.data
    
    assert data['id'] == asset.id
    assert data['user']['id'] == user.id  # User is serialized as a nested object
    assert data['project_id'] == project.id
    assert data['session_id'] == session.id
    assert data['envelope_ids'] == [envelope.id]
    assert data['language_id'] == language.id
    assert data['media_type'] == 'audio'
    assert data['audio_length_in_seconds'] == 10.0  # Converted from nanoseconds
    assert data['volume'] == 1.0
    assert data['weight'] == 1.0
    assert data['latitude'] == 10.0
    assert data['longitude'] == 20.0
    assert data['shape'] == {
        'type': 'MultiPolygon',
        'coordinates': [[[[10.0, 20.0], [10.0, 20.1], [10.1, 20.1], [10.1, 20.0], [10.0, 20.0]]]]
    }

@pytest.mark.django_db
def test_audiotrack_serializer_with_all_fields():
    project = baker.make(models.Project)
    audiotrack = baker.make(models.Audiotrack,
        project=project,
        minduration=1e9,
        maxduration=2e9,
        mindeadair=0.5e9,
        maxdeadair=1e9,
        minfadeintime=0.1e9,
        maxfadeintime=0.2e9,
        minfadeouttime=0.1e9,
        maxfadeouttime=0.2e9,
        minpanduration=0.5e9,
        maxpanduration=1e9
    )
    serializer = serializers.AudiotrackSerializer(audiotrack)
    data = serializer.data
    assert data['minduration'] == 1.0
    assert data['maxduration'] == 2.0
    assert data['mindeadair'] == 0.5
    assert data['maxdeadair'] == 1.0
    assert data['minfadeintime'] == 0.1
    assert data['maxfadeintime'] == 0.2
    assert data['minfadeouttime'] == 0.1
    assert data['maxfadeouttime'] == 0.2
    assert data['minpanduration'] == 0.5
    assert data['maxpanduration'] == 1.0
    assert data['project_id'] == project.id

@pytest.mark.django_db
def test_envelope_serializer_with_assets():
    session = baker.make(models.Session)
    envelope = baker.make(models.Envelope, session=session)
    assets = [baker.make(models.Asset) for _ in range(3)]
    envelope.assets.set(assets)
    serializer = serializers.EnvelopeSerializer(envelope)
    data = serializer.data
    assert data['asset_ids'] == [asset.id for asset in assets]
    assert data['session_id'] == session.id

@pytest.mark.django_db
def test_event_serializer_with_all_fields():
    session = baker.make(models.Session)
    event = baker.make(models.Event,
        session=session,
        tags='1,2,3',
        latitude='10.0',
        longitude='20.0'
    )
    serializer = serializers.EventSerializer(event)
    data = serializer.data
    assert data['session_id'] == session.id
    assert data['tag_ids'] == [1, 2, 3]
    assert data['latitude'] == 10.0
    assert data['longitude'] == 20.0

@pytest.mark.django_db
def test_language_serializer_with_all_fields():
    language = baker.make(models.Language, language_code='fr', name='French')
    serializer = serializers.LanguageSerializer(language)
    data = serializer.data
    assert data['language_code'] == 'fr'
    assert data['name'] == 'French'

@pytest.mark.django_db
def test_listen_event_serializer_with_all_fields():
    session = baker.make(models.Session)
    asset = baker.make(models.Asset)
    listen_event = baker.make(models.ListeningHistoryItem,
        session=session,
        asset=asset,
        starttime='2020-01-01T00:00:00Z',
        duration=10.0
    )
    serializer = serializers.ListenEventSerializer(listen_event)
    data = serializer.data
    assert data['session_id'] == session.id
    assert data['asset_id'] == asset.id
    assert data['start_time'] == '2020-01-01T00:00:00Z'
    assert data['project_id'] == session.project_id

@pytest.mark.django_db
def test_localized_string_serializer_with_all_fields():
    language = baker.make(models.Language, language_code='fr')
    loc_string = baker.make(models.LocalizedString,
        language=language,
        localized_string='Test String'
    )
    serializer = serializers.LocalizedStringSerializer(loc_string)
    data = serializer.data
    assert data['text'] == 'Test String'
    assert data['language_id'] == language.id
    assert data['language'] == 'fr'

@pytest.mark.django_db
def test_project_serializer_with_all_fields():
    lang = baker.make(models.Language, language_code='en')
    project = baker.make(models.Project)
    project.languages.set([lang])
    serializer = serializers.ProjectSerializer(project)
    data = serializer.data
    assert data['language_ids'] == [lang.id]

@pytest.mark.django_db
def test_project_chooser_serializer_with_all_fields():
    language = baker.make(models.Language, language_code='fr')
    loc_string = baker.make(models.LocalizedString,
        language=language,
        localized_string='Project Description'
    )
    project = baker.make(models.Project)
    project.description_loc.set([loc_string])
    serializer = serializers.ProjectChooserSerializer(project, context={'language_code': 'fr'})
    data = serializer.data
    assert data['project_id'] == project.id
    assert data['description_loc'] == 'Project Description'
    assert data['thumbnail_url'] == f'{settings.MEDIA_URL}project{project.id}-thumb.png'

@pytest.mark.django_db
def test_project_group_serializer_with_all_fields():
    group = baker.make(models.ProjectGroup)
    projects = [baker.make(models.Project) for _ in range(3)]
    group.projects.set(projects)
    serializer = serializers.ProjectGroupSerializer(group)
    data = serializer.data
    
    # Check all fields from the model
    assert data['id'] == group.id
    assert set(data['project_ids']) == set(project.id for project in projects)

@pytest.mark.django_db
def test_session_serializer_with_all_fields():
    language = baker.make(models.Language)
    project = baker.make(models.Project)
    session = baker.make(models.Session,
        language=language,
        project=project,
        timezone='+0200'
    )
    serializer = serializers.SessionSerializer(session)
    data = serializer.data
    assert data['language_id'] == language.id
    assert data['project_id'] == project.id
    assert data['timezone'] == '+0200'

@pytest.mark.django_db
def test_speaker_serializer_with_children():
    project = baker.make(models.Project)
    parent = baker.make(models.Speaker, project=project)
    children = [baker.make(models.Speaker, project=project) for _ in range(3)]
    parent.children.add(*children)
    serializer = serializers.SpeakerSerializer(parent)
    data = serializer.data
    assert data['project_id'] == project.id
    assert set(data['children']) == set([child.id for child in children])

@pytest.mark.django_db
def test_tag_serializer_with_all_fields():
    project = baker.make(models.Project)
    category = baker.make(models.TagCategory)
    language = baker.make(models.Language, language_code='en')
    tag = baker.make(models.Tag,
        project=project,
        tag_category=category,
        value='Test Tag'
    )
    loc_msg = baker.make(models.LocalizedString,
        language=language,
        localized_string='Test Message'
    )
    loc_desc = baker.make(models.LocalizedString,
        language=language,
        localized_string='Test Description'
    )
    tag.loc_msg.set([loc_msg])
    tag.loc_description.set([loc_desc])
    serializer = serializers.TagSerializer(tag, context={'session': None})
    data = serializer.data
    assert data['project_id'] == project.id
    assert data['tag_category_id'] == category.id
    assert data['value'] == 'Test Tag'
    assert data['msg_loc'] == 'Test Message'
    assert data['description_loc'] == 'Test Description'

@pytest.mark.django_db
def test_tag_category_serializer_with_all_fields():
    category = baker.make(models.TagCategory, name='Test Category')
    serializer = serializers.TagCategorySerializer(category)
    data = serializer.data
    assert data['name'] == 'Test Category'

@pytest.mark.django_db
def test_tag_relationship_serializer_with_all_fields():
    tag = baker.make(models.Tag)
    parent_tag = baker.make(models.Tag)
    parent_rel = baker.make(models.TagRelationship, tag=parent_tag, parent=None)
    child_rel = baker.make(models.TagRelationship, tag=tag, parent=parent_rel)
    serializer = serializers.TagRelationshipSerializer(child_rel)
    data = serializer.data
    assert data['tag_id'] == tag.id
    assert data['parent_id'] == parent_rel.id

@pytest.mark.django_db
def test_timed_asset_serializer_with_all_fields():
    project = baker.make(models.Project)
    asset = baker.make(models.Asset)
    timed = baker.make(models.TimedAsset,
        project=project,
        asset=asset,
        start=1.0,
        end=2.0
    )
    serializer = serializers.TimedAssetSerializer(timed)
    data = serializer.data
    assert data['project_id'] == project.id
    assert data['asset_id'] == asset.id
    assert data['start'] == 1.0
    assert data['end'] == 2.0

@pytest.mark.django_db
def test_uiconfig_serializer_with_all_fields():
    # Ensure English language exists
    models.Language.objects.filter(language_code='en').delete()  # Clean up any existing English language
    lang = baker.make(models.Language, language_code='en')
    
    tag_category = baker.make(models.TagCategory, name='TestCat')
    group = baker.make(models.UIGroup, tag_category=tag_category)
    
    # Create and associate localized string for header text
    header_loc = baker.make(models.LocalizedString,
        language=lang,
        localized_string='Header Text'
    )
    group.header_text_loc.set([header_loc])
    
    # Create tag and UIItem
    tag = baker.make(models.Tag)
    tag_loc = baker.make(models.LocalizedString,
        language=lang,
        localized_string='Tag Text'
    )
    tag.loc_msg.set([tag_loc])
    
    item = baker.make(models.UIItem, ui_group=group, tag=tag, active=True)
    
    serializer = serializers.UIConfigSerializer(group, context={'mode': 'listen'})
    data = serializer.data
    
    assert data['header_display_text'] == 'Header Text'
    assert len(data['display_items']) == 1
    assert data['display_items'][0]['tag_id'] == tag.id
    assert data['display_items'][0]['tag_display_text'] == 'Tag Text'
    assert data['display_items'][0]['parent_id'] is None  # listen mode flattens parent_id

@pytest.mark.django_db
def test_uiconfig_item_serializer_with_all_fields():
    # Ensure English language exists
    models.Language.objects.filter(language_code='en').delete()  # Clean up any existing English language
    lang = baker.make(models.Language, language_code='en')
    
    # Create tag with localized message
    tag = baker.make(models.Tag)
    tag_loc = baker.make(models.LocalizedString,
        language=lang,
        localized_string='Tag Text'
    )
    tag.loc_msg.set([tag_loc])
    
    # Create UIItem with parent
    parent_item = baker.make(models.UIItem, tag=tag, default=True, active=True)
    item = baker.make(models.UIItem, tag=tag, default=True, active=True, parent=parent_item)
    
    serializer = serializers.UIConfigItemSerializer(item, context={'mode': 'listen'})
    data = serializer.data
    
    assert data['tag_id'] == tag.id
    assert data['tag_display_text'] == 'Tag Text'
    assert data['parent_id'] is None  # listen mode flattens parent_id
    assert data['default_state'] is True

@pytest.mark.django_db
def test_uielement_serializer_with_all_fields():
    name = baker.make(models.UIElementName)
    project = baker.make(models.Project)
    language = baker.make(models.Language)
    loc = baker.make(models.LocalizedString, language=language)
    element = baker.make(models.UIElement,
        uielementname=name,
        project=project
    )
    element.label_text_loc.add(loc)
    serializer = serializers.UIElementSerializer(element)
    data = serializer.data
    assert data['uielementname_id'] == name.id
    assert data['project_id'] == project.id
    assert data['label_text_loc_ids'] == [loc.id]

@pytest.mark.django_db
def test_uielement_project_serializer_with_all_fields():
    name = baker.make(models.UIElementName, name='test_element')
    language = baker.make(models.Language, language_code='en')
    loc = baker.make(models.LocalizedString,
        language=language,
        localized_string='Test Label'
    )
    element = baker.make(models.UIElement,
        uielementname=name,
        variant='_variant',
        file_extension='png'
    )
    element.label_text_loc.add(loc)
    serializer = serializers.UIElementProjectSerializer(element, context={'lc': 'en'})
    data = serializer.data
    assert 'test_element' in data
    element_data = data['test_element']
    assert element_data['file_name'] == 'test_element_variant.png'
    assert element_data['label_text'] == 'Test Label'

@pytest.mark.django_db
def test_uielement_name_serializer_with_all_fields():
    name = baker.make(models.UIElementName, name='Test Name')
    serializer = serializers.UIElementNameSerializer(name)
    data = serializer.data
    assert data['name'] == 'Test Name'

@pytest.mark.django_db
def test_uigroup_serializer_with_all_fields():
    # Ensure English language exists
    models.Language.objects.filter(language_code='en').delete()  # Clean up any existing English language
    lang = baker.make(models.Language, language_code='en')
    
    tag_category = baker.make(models.TagCategory)
    project = baker.make(models.Project)
    group = baker.make(models.UIGroup, tag_category=tag_category, project=project)
    tag = baker.make(models.Tag)
    item = baker.make(models.UIItem, ui_group=group, tag=tag)
    serializer = serializers.UIGroupSerializer(group)
    data = serializer.data
    assert 'ui_items' in data
    assert len(data['ui_items']) == 1
    assert data['tag_category_id'] == tag_category.id
    assert data['project_id'] == project.id

@pytest.mark.django_db
def test_uiitem_serializer_with_all_fields():
    group = baker.make(models.UIGroup)
    tag = baker.make(models.Tag)
    parent = baker.make(models.UIItem, ui_group=group)
    item = baker.make(models.UIItem,
        ui_group=group,
        tag=tag,
        parent=parent
    )
    serializer = serializers.UIItemSerializer(item)
    data = serializer.data
    assert data['ui_group_id'] == group.id
    assert data['tag_id'] == tag.id
    assert data['parent_id'] == parent.id

@pytest.mark.django_db
def test_user_serializer_with_all_fields():
    data = {
        'device_id': 'test-device-123',
        'client_type': 'test-client',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com'
    }
    serializer = serializers.UserSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.username is not None
    assert user.first_name == 'Test'
    assert user.last_name == 'User'
    assert user.email == 'test@example.com'
    assert user.userprofile.device_id == 'test-device-123'
    assert user.userprofile.client_type == 'test-client'

@pytest.mark.django_db
def test_user_info_serializer_with_all_fields():
    user = baker.make(User,
        first_name='Test',
        last_name='User',
        email='test@example.com'
    )
    user.userprofile.device_id = 'test-device-123'
    user.userprofile.client_type = 'test-client'
    user.userprofile.save()
    serializer = serializers.UserInfoSerializer(user)
    data = serializer.data
    assert data['id'] == user.id
    assert data['username'] == user.username
    assert data['first_name'] == 'Test'
    assert data['last_name'] == 'User'
    assert data['email'] == 'test@example.com'
    assert data['device_id'] == 'test-device-123'
    assert data['client_type'] == 'test-client'

@pytest.mark.django_db
def test_vote_serializer_with_all_fields():
    user = baker.make(User)
    asset = baker.make(models.Asset)
    session = baker.make(models.Session)
    vote = baker.make(models.Vote,
        voter=user,
        asset=asset,
        session=session,
        value=1
    )
    serializer = serializers.VoteSerializer(vote)
    data = serializer.data
    assert data['voter_id'] == user.id
    assert data['asset_id'] == asset.id
    assert data['session_id'] == session.id
    assert 'asset_votes' in data

@pytest.mark.django_db
def test_vote_summary_serializer_with_all_fields():
    asset = baker.make(models.Asset)
    vote = baker.make(models.Vote, asset=asset, value=1)
    serializer = serializers.VoteSummarySerializer(vote, context={'type': 'like'})
    data = serializer.data
    assert data['asset_id'] == asset.id
    assert 'asset_votes' in data

@pytest.mark.django_db
def test_select_localized_string_with_all_cases():
    session = baker.make(models.Session)
    lang = baker.make(models.Language, language_code='fr')
    session.language = lang
    session.save()
    loc = baker.make(models.LocalizedString,
        language=lang,
        localized_string='French Text'
    )
    result = serializers._select_localized_string([loc.id], session=session)
    assert result == 'French Text'

    lang_en = baker.make(models.Language, language_code='en')
    loc_en = baker.make(models.LocalizedString,
        language=lang_en,
        localized_string='English Text'
    )
    result = serializers._select_localized_string([loc_en.id], session=None)
    assert result == 'English Text'

    result = serializers._select_localized_string([loc.id], session=None)
    assert result is None

@pytest.mark.django_db
def test_select_localized_string_with_code_with_all_cases():
    # Ensure English language exists
    models.Language.objects.filter(language_code='en').delete()  # Clean up any existing English language
    lang_en = baker.make(models.Language, language_code='en')
    loc_en = baker.make(models.LocalizedString,
        language=lang_en,
        localized_string='English Text'
    )
    
    lang_fr = baker.make(models.Language, language_code='fr')
    loc_fr = baker.make(models.LocalizedString,
        language=lang_fr,
        localized_string='French Text'
    )
    
    # Test French text when French is available
    result = serializers._select_localized_string_with_code([loc_fr.id], language_code='fr')
    assert result == 'French Text'
    
    # Test fallback to English when French is not available
    result = serializers._select_localized_string_with_code([loc_en.id, loc_fr.id], language_code='fr')
    assert result == 'French Text'  # Should get French text since it's available
    
    # Test fallback to English when no matching language is found
    result = serializers._select_localized_string_with_code([loc_en.id, loc_fr.id], language_code='de')
    assert result == 'English Text'  # Should fall back to English
