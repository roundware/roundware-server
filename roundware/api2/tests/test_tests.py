import pytest
from model_bakery import baker
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from roundware.rw.models import (
    ListeningHistoryItem, Asset, Project, Audiotrack, Session,
    Envelope, Speaker, LocalizedString, UIGroup, UIItem,
    Language, Tag, TagCategory
)

TEST_POLYGONS = {
    "crazy_shape": "MULTIPOLYGON(((-0.774183051414968 -0.120296667618684,-0.697181433024807 0.197879831012361,-0.52645517133469 0.200040922932489,-0.444333678369823 -0.0571290155627506,-0.468105689491232 -0.245144012613892,-0.774183051414968 -0.120296667618684)),((-1.25042096457759 0.204363106772745,-1.01702303720376 0.504754883670546,-0.599932296619044 0.625776031197718,-0.152586269152534 0.448566493747217,0.0354287278986072 0.00122046628070716,-0.109364430749973 -0.30349349445735,-0.340601266203676 -0.487186307668236,-0.811719304791594 -0.487186307668236,-1.0969834382485 -0.331587689419015,-1.25042096457759 0.204363106772745),(-0.774183051414968 -0.120296667618684,-0.811719304791594 -0.275399299495685,-0.504844252133409 -0.374809527821576,-0.314668163162139 -0.327265505578759,-0.239029945957657 -0.0506457398023664,-0.362212185404957 0.325384254299917,-0.796591661350698 0.35563954118171,-0.880874246235692 0.122241613807879,-0.958673555360303 -0.0917064862847996,-0.889518613916205 -0.0247126367608296,-0.796591661350698 -0.111156313565952,-0.774183051414968 -0.120296667618684)))",
    "square": "MULTIPOLYGON(((10 10, 10 20, 20 20, 20 10, 10 10)))"
}

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def setup_test_data():
    # Create basic test data
    english = baker.make(Language, language_code='en')
    spanish = baker.make(Language, language_code='es')
    english_msg = baker.make(LocalizedString, localized_string="One", language=english)
    spanish_msg = baker.make(LocalizedString, localized_string="Uno", language=spanish)
    
    # Create project
    project = baker.make(
        Project,
        name='Uno',
        recording_radius=10,
        audio_format='ogg',
        demo_stream_message_loc=[english_msg, spanish_msg],
        out_of_range_url='http://rw.com:8000/outofrange.mp3',
        geo_listen_enabled=True
    )
    
    # Create session
    session = baker.make(Session, project=project, language=english)
    
    # Create tag categories
    tagcat1 = baker.make(TagCategory, name='gender')
    tagcat2 = baker.make(TagCategory, name='age')
    tagcat3 = baker.make(TagCategory, name='color')
    
    # Create tags
    tag1 = baker.make(
        Tag,
        project=project,
        tag_category=tagcat1,
        value='male',
        loc_description=[english_msg, spanish_msg],
        loc_msg=[english_msg, spanish_msg]
    )
    
    tag2 = baker.make(
        Tag,
        project=project,
        tag_category=tagcat2,
        value='young'
    )
    
    tag3 = baker.make(
        Tag,
        project=None,
        tag_category=tagcat3,
        value='red'
    )
    
    # Create UI groups
    uigroup1 = baker.make(UIGroup, project=project, ui_mode=UIGroup.LISTEN, tag_category=tagcat1)
    uigroup2 = baker.make(UIGroup, project=project, ui_mode=UIGroup.LISTEN, tag_category=tagcat2)
    uigroup3 = baker.make(UIGroup, project=project, ui_mode=UIGroup.SPEAK, tag_category=tagcat1)
    uigroup4 = baker.make(UIGroup, project=project, ui_mode=UIGroup.SPEAK, tag_category=tagcat2)
    uigroup5 = baker.make(UIGroup, project=project, ui_mode=UIGroup.SPEAK, tag_category=tagcat3)
    
    # Create UI items
    uiitem1 = baker.make(UIItem, ui_group=uigroup1, tag=tag1, active=True)
    uiitem2 = baker.make(UIItem, ui_group=uigroup1, tag=tag2, active=True)
    
    # Create assets
    asset1 = baker.make(
        Asset,
        project=project,
        audiolength=5000000000,
        volume=0.9,
        latitude='0.1',
        longitude='0.1',
        language=english,
        tags=(tag1,)
    )
    
    asset2 = baker.make(
        Asset,
        project=project,
        audiolength=10000000000,
        language=english,
        tags=(tag1,)
    )
    
    # Create envelopes
    envelope1 = baker.make(Envelope, session=session, assets=[asset1])
    envelope2 = baker.make(Envelope, session=session, assets=[asset2])
    
    # Create listening history
    history1 = baker.make(ListeningHistoryItem, asset=asset1, session=session)
    history2 = baker.make(ListeningHistoryItem, asset=asset2, session=session)
    
    # Create audio elements
    track1 = baker.make(Audiotrack, project=project)
    speaker1 = baker.make(
        Speaker,
        project=project,
        shape=TEST_POLYGONS["crazy_shape"],
        attenuation_distance=100,
        activeyn=True
    )
    
    return {
        'project': project,
        'session': session,
        'asset1': asset1,
        'asset2': asset2,
        'english': english,
        'spanish': spanish
    }

@pytest.fixture
def authenticated_client(api_client):
    """Fixture to create an authenticated client"""
    url = reverse('user-list')
    data = {
        "device_id": "12891038109281",
        "client_type": "phone",
        "client_system": "iOS"
    }
    response = api_client.post(url, data, format='json')
    token = response.data["token"]
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return api_client

@pytest.mark.django_db
class TestAPIEndpoints:
    def test_users_post(self, api_client):
        url = reverse('user-list')
        data = {
            "device_id": "12891038109281",
            "client_type": "phone",
            "client_system": "iOS"
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] is not None
        assert response.data["token"] is not None

    def test_sessions_post(self, authenticated_client, setup_test_data):
        url = reverse('session-list')
        data = {
            "timezone": "-0500",
            "project_id": setup_test_data['project'].id,
            "client_system": "iOS",
            "language_id": setup_test_data['english'].id,
            "starttime": "2024-03-20T00:00:00Z"
        }
        response = authenticated_client.post(url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print("Response data:", response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["language_id"] == setup_test_data['english'].id
        assert response.data["geo_listen_enabled"] is True
        assert response.data["timezone"] == data["timezone"]
        assert response.data["client_system"] == data["client_system"]
        assert response.data["project_id"] == data["project_id"]
        assert response.data["id"] is not None
        
        # Test with geo_listen_enabled set to False
        data["geo_listen_enabled"] = False
        response = authenticated_client.post(url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print("Response data:", response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["geo_listen_enabled"] is False

    def test_projects_get(self, authenticated_client, setup_test_data):
        url = f"{reverse('project-detail', args=[setup_test_data['project'].id])}?session_id={setup_test_data['session'].id}"
        response = authenticated_client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert "out_of_range_message" in response.data
        assert "out_of_range_message_loc" not in response.data
        assert setup_test_data['project'].id == response.data["id"]

    def test_projects_tags_get(self, authenticated_client, setup_test_data):
        url = reverse('project-tags', args=[setup_test_data['project'].id])
        response = authenticated_client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]["project_id"] == setup_test_data['project'].id

    def test_projects_assets_get(self, authenticated_client, setup_test_data):
        url = reverse('project-assets', args=[setup_test_data['project'].id])
        response = authenticated_client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]["project_id"] == setup_test_data['project'].id

    def test_vote_assets_post(self, authenticated_client, setup_test_data):
        # Create a session via the API for the authenticated user
        session_data = {
            "timezone": "-0500",
            "project_id": setup_test_data['project'].id,
            "client_system": "iOS",
            "geo_listen_enabled": True,
            "language_id": setup_test_data['english'].id
        }
        session_response = authenticated_client.post(reverse('session-list'), session_data, format='json')
        assert session_response.status_code == status.HTTP_200_OK
        session_id = session_response.data["id"]

        # Get the authenticated user
        user = get_user_model().objects.get(userprofile__device_id="12891038109281")
        
        data = {
            "device_id": "12891038109281",
            "session_id": session_id,
            "vote_type": "rate",
            "value": 2
        }
        response = authenticated_client.post(f'/api/2/assets/{setup_test_data["asset1"].id}/votes/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data["voter_id"] == user.id
        assert response.data["session_id"] == data["session_id"]
        assert response.data["type"] == data["vote_type"]
        assert response.data["value"] == data["value"]
        assert response.data["id"] is not None

    def test_vote_assets_get(self, authenticated_client, setup_test_data):
        # First create a vote
        data = {
            "device_id": "12891038109281",
            "session_id": setup_test_data['session'].id,
            "vote_type": "rate",
            "value": 2
        }
        authenticated_client.post(f'/api/2/assets/{setup_test_data["asset1"].id}/votes/', data, format='json')
        
        # Then get the votes
        response = authenticated_client.get(f'/api/2/assets/{setup_test_data["asset1"].id}/votes/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["type"] == "rate"
        assert response.data[0]["avg"] == 2

    def test_assets_random_get(self, authenticated_client, setup_test_data):
        # Test with audiolength <= 8
        data = {
            "mediatype": "audio",
            "project_id": setup_test_data['project'].id,
            "audiolength__lte": 8,
            "limit": 2
        }
        response = authenticated_client.get('/api/2/assets/random/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        
        # Test with audiolength <= 12
        data["audiolength__lte"] = 12
        response = authenticated_client.get('/api/2/assets/random/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_token_required(self, api_client, setup_test_data):
        # Test endpoints without token
        api_client.credentials(HTTP_AUTHORIZATION='')
        
        # Test sessions endpoint
        url = reverse('session-list')
        data = {"timezone": "-0500", "project_id": 1, "client_system": "iOS"}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test projects endpoint
        url = reverse('project-detail', args=[setup_test_data['project'].id])
        response = api_client.get(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test project tags endpoint
        url = reverse('project-tags', args=[setup_test_data['project'].id])
        response = api_client.get(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test project assets endpoint
        url = reverse('project-assets', args=[setup_test_data['project'].id])
        response = api_client.get(url, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test vote assets endpoint
        data = {"device_id": "12891038109281", "session_id": 1, "vote_type": "rate", "value": 2}
        response = api_client.post('/api/2/assets/1/votes/', data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_api2_in_order(self, authenticated_client, setup_test_data):
        """Test all API endpoints in order with proper authentication"""
        
        # Test sessions endpoint
        url = reverse('session-list')
        data = {
            "timezone": "-0500",
            "project_id": setup_test_data['project'].id,
            "client_system": "iOS",
            "language_id": setup_test_data['english'].id
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data["language_id"] == setup_test_data['english'].id
        assert response.data["geo_listen_enabled"] is True
        session_id = response.data["id"]
        
        # Test projects endpoint
        url = f"{reverse('project-detail', args=[setup_test_data['project'].id])}?session_id={session_id}"
        response = authenticated_client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert "out_of_range_message" in response.data
        
        # Test project tags endpoint
        url = reverse('project-tags', args=[setup_test_data['project'].id])
        response = authenticated_client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # Test project assets endpoint
        url = reverse('project-assets', args=[setup_test_data['project'].id])
        response = authenticated_client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # Test vote assets endpoint
        data = {
            "device_id": "12891038109281",
            "session_id": session_id,
            "vote_type": "rate",
            "value": 2
        }
        response = authenticated_client.post(f'/api/2/assets/{setup_test_data["asset1"].id}/votes/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        # Test get votes endpoint
        response = authenticated_client.get(f'/api/2/assets/{setup_test_data["asset1"].id}/votes/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["type"] == "rate"
        assert response.data[0]["avg"] == 2
        
        # Test random assets endpoint
        data = {
            "mediatype": "audio",
            "project_id": setup_test_data['project'].id,
            "audiolength__lte": 12,
            "limit": 2
        }
        response = authenticated_client.get('/api/2/assets/random/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        # Note: Some endpoints cannot be tested currently
        # - streams_post
        # - streams_patch
        # - streams_heartbeat_post
        # - streams_next_post
        # - streams_current_get
