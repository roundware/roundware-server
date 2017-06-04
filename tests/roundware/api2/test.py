# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.


from __future__ import unicode_literals
import datetime

from model_mommy import mommy
from model_mommy.generators import gen_file_field

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from roundware.rw.models import (ListeningHistoryItem, Asset, Project,
                                 Audiotrack, Session, Envelope,
                                 Speaker, LocalizedString, UIGroup, UIItem,
                                 Language, Tag, TagCategory)
from roundware.settings import DEFAULT_SESSION_ID

from rest_framework import status
from rest_framework.test import APITestCase

TEST_POLYGONS = {
    "crazy_shape": "MULTIPOLYGON(((-0.774183051414968 -0.120296667618684,-0.697181433024807 0.197879831012361,-0.52645517133469 0.200040922932489,-0.444333678369823 -0.0571290155627506,-0.468105689491232 -0.245144012613892,-0.774183051414968 -0.120296667618684)),((-1.25042096457759 0.204363106772745,-1.01702303720376 0.504754883670546,-0.599932296619044 0.625776031197718,-0.152586269152534 0.448566493747217,0.0354287278986072 0.00122046628070716,-0.109364430749973 -0.30349349445735,-0.340601266203676 -0.487186307668236,-0.811719304791594 -0.487186307668236,-1.0969834382485 -0.331587689419015,-1.25042096457759 0.204363106772745),(-0.774183051414968 -0.120296667618684,-0.811719304791594 -0.275399299495685,-0.504844252133409 -0.374809527821576,-0.314668163162139 -0.327265505578759,-0.239029945957657 -0.0506457398023664,-0.362212185404957 0.325384254299917,-0.796591661350698 0.35563954118171,-0.880874246235692 0.122241613807879,-0.958673555360303 -0.0917064862847996,-0.889518613916205 -0.0247126367608296,-0.796591661350698 -0.111156313565952,-0.774183051414968 -0.120296667618684)))",
    "square": "MULTIPOLYGON(((10 10, 10 20, 20 20, 20 10, 10 10)))"
}

def validated_file_field_gen():
    return gen_file_field()

class TestServer(APITestCase):

    """ test api.py methods
    """

    def setUp(self):
        super(type(self), TestServer).setUp(self)

        self.maxDiff = None

        generator_dict = {
            'validatedfile.fields.ValidatedFileField':
            validated_file_field_gen
        }
        # can't set this directly in settings: db ENGINE not yet available
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)

        # setup basics
        self.default_session = mommy.make(Session)
        self.english = mommy.make(Language, language_code='en')
        self.spanish = mommy.make(Language, language_code='es')
        self.english_msg = mommy.make(LocalizedString, localized_string="One",
                                      language=self.english)
        self.spanish_msg = mommy.make(LocalizedString, localized_string="Uno",
                                      language=self.spanish)

        # create project and session
        self.project1 = mommy.make(
            Project,
            id = 1,
            name = 'Uno',
            recording_radius = 10,
            audio_format = 'ogg',
            demo_stream_message_loc = [self.english_msg, self.spanish_msg],
            out_of_range_url='http://rw.com:8000/outofrange.mp3',
            geo_listen_enabled=True
        )

        self.session = mommy.make(
            Session,
            project=self.project1,
            language=self.english
        )

        # setup tag categories
        self.tagcat1 = mommy.make(TagCategory, name='gender')
        self.tagcat2 = mommy.make(TagCategory, name='age')
        self.tagcat3 = mommy.make(TagCategory, name='color')

        # setup tags
        self.tag1 = mommy.make(
            Tag,
            project = self.project1,
            tag_category = self.tagcat1,
            value = 'male',
            loc_description = [self.english_msg, self.spanish_msg],
            loc_msg = [self.english_msg, self.spanish_msg],
            data = None,
            filter = "",
            location = None
        )

        self.tag2 = mommy.make(
            Tag,
            project = self.project1,
            tag_category=self.tagcat2,
            value = 'young'
        )

        self.tag3 = mommy.make(
            Tag,
            project = None, # this tag should not appear in projects_tags_get
            tag_category = self.tagcat3,
            value = 'red'
        )

        # setup ui_groups
        self.uigroup1 = mommy.make(
            UIGroup,
            project=self.project1,
            ui_mode=UIGroup.LISTEN,
            tag_category=self.tagcat1
        )

        self.uigroup2 = mommy.make(
            UIGroup,
            project=self.project1,
            ui_mode=UIGroup.LISTEN,
            tag_category=self.tagcat2
        )

        self.uigroup3 = mommy.make(
            UIGroup,
            project=self.project1,
            ui_mode=UIGroup.SPEAK,
            tag_category=self.tagcat1
        )

        self.uigroup4 = mommy.make(
            UIGroup,
            project=self.project1,
            ui_mode=UIGroup.SPEAK,
            tag_category=self.tagcat2
        )

        self.uigroup5 = mommy.make(
            UIGroup,
            project=self.project1,
            ui_mode=UIGroup.SPEAK,
            tag_category=self.tagcat3
        )

        # setup ui_items
        self.uiitem1 = mommy.make(
            UIItem,
            ui_group=self.uigroup1,
            tag=self.tag1,
            active=True
        )

        self.uiitem2 = mommy.make(
            UIItem,
            ui_group=self.uigroup1,
            tag=self.tag2,
            active=True
        )

        # setup assets and envelopes
        self.asset1 = mommy.make(Asset, project=self.project1, id=1,
                                 audiolength=5000000000, volume=0.9,
                                 created=datetime.datetime(
                                     2013, 11, 21, 21, 3, 6, 616402),
                                 latitude='0.1', longitude='0.1',
                                 language=self.english,
                                 tags=(self.tag1,))
        self.asset2 = mommy.make(Asset, project=self.project1, id=2,
                                 audiolength=10000000000,
                                 language=self.english,
                                 tags=(self.tag1,))
        self.envelope1 = mommy.make(Envelope, session=self.session,
                                    assets=[self.asset1, ])
        self.envelope2 = mommy.make(Envelope, session=self.session,
                                    assets=[self.asset2, ])

        # setup audio elements
        self.history1 = mommy.make(ListeningHistoryItem, asset=self.asset1,
                                   session=self.session,
                                   starttime=datetime.datetime(
                                       2013, 11, 21, 17, 29, 10, 173061),
                                   duration=5000000)
        self.history2 = mommy.make(ListeningHistoryItem, asset=self.asset2,
                                   session=self.session,
                                   starttime=datetime.datetime(
                                       2013, 11, 21, 17, 29, 44, 610672),
                                   duration=6000000)
        self.track1 = mommy.make(Audiotrack, project=self.project1, id=1)
        self.speaker1 = mommy.make(Speaker, project=self.project1,
                                   shape=TEST_POLYGONS["crazy_shape"],
                                   attenuation_distance=100, activeyn=True)

    def test_api2_in_order(self):
        self.users_post()
        self.sessions_post()
        self.projects_get()
        self.projects_tags_get()
        self.projects_assets_get()
        self.vote_assets_post()
        self.vote_assets_get()
        self.assets_random_get()

        # some endpoints cannot be tested currently
        # self.streams_post()
        # self.streams_patch()
        # self.streams_heartbeat_post()
        # self.streams_next_post()
        # self.streams_current_get()

        self.ensure_token_required()

    def users_post(self):
        url = reverse('user-list')
        data = {"device_id": "12891038109281",
                "client_type": "phone",
                "client_system": "iOS"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check that a username was generated and token returned
        self.assertIsNotNone(response.data["username"])
        self.assertIsNotNone(response.data["token"])
        # set the token for later requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data["token"])

    def sessions_post(self):
        url = reverse('session-list')
        # first pass no geo_listen_enabled
        data = {"timezone": "-0500",
                "project_id": 1,
                "client_system": "iOS"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # language wasn't provided, so should be set default to "en"
        self.assertEqual(response.data["language"], "en")
        # geo_listen_enabled not provided, so set to project.geo_listen_enabled value
        self.assertEqual(response.data["geo_listen_enabled"], True)
        # check returned data matches data provided
        self.assertEqual(response.data["timezone"], data["timezone"])
        self.assertEqual(response.data["client_system"], data["client_system"])
        self.assertEqual(response.data["project_id"], data["project_id"])
        self.assertIsNotNone(response.data["session_id"])
        # save session_id for later requests
        self.session_id = response.data["session_id"]

        # now pass geo_listen_enabled
        data = {"timezone": "-0500",
                "project_id": 1,
                "client_system": "iOS",
                "geo_listen_enabled": False}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check geo_listen_enabled returns same as passed param, not project value
        self.assertEqual(response.data["geo_listen_enabled"], False)

    def projects_get(self):
        url = "%s?session_id=%s" % (reverse('project-detail', args=[self.project1.id]), self.session_id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ensure _loc fields are transformed
        self.assertIn("out_of_range_message", response.data)
        self.assertNotIn("out_of_range_message_loc", response.data)
        self.assertEqual(self.project1.id, response.data["id"])

    def projects_tags_get(self):
        # Strictly speaking, session_id is necessary only for localization purposes
        # url = "%s?session_id=%s" % (reverse('project-tags', args=[self.project1.id]), self.session_id)
        url = "%s" % (reverse('project-tags', args=[self.project1.id]))
        data = {}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # { "tags" : [] }
        self.assertEqual(len(response.data["tags"]), 2) # one tag excluded
        self.assertEqual(response.data["tags"][0]["project_id"], self.project1.id)

    def projects_assets_get(self):
        url = reverse('project-assets', args=[self.project1.id])
        data = {}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["project"], self.project1.id)

    def vote_assets_post(self):
        data = {"device_id": "12891038109281",
                "session_id": self.session_id,
                "vote_type": "rate",
                "value": 2}
        response = self.client.post('/api/2/assets/1/votes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check returned data matches data provided
        User = get_user_model()
        user_id = User.objects.filter(userprofile__device_id=data["device_id"]) \
                              .values_list('id', flat=True)[0]
        self.assertEqual(response.data["voter_id"], user_id)
        self.assertEqual(response.data["session_id"], data["session_id"])
        self.assertEqual(response.data["type"], data["vote_type"])
        self.assertEqual(response.data["value"], data["value"])
        self.assertIsNotNone(response.data["id"])

    def vote_assets_get(self):
        response = self.client.get('/api/2/assets/1/votes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check returned data matches votes provided
        self.assertEqual(response.data[0]["type"], "rate")
        self.assertEqual(response.data[0]["avg"], 2)

    def assets_random_get(self):
        data = {"mediatype": "audio",
                "project_id": self.project1.id,
                "audiolength__lte": 8,
                "limit": 2}
        response = self.client.get('/api/2/assets/random/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        data = {"mediatype": "audio",
                "project_id": self.project1.id,
                "audiolength__lte": 12,
                "limit": 2}
        response = self.client.get('/api/2/assets/random/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def ensure_token_required(self):
        self.client.credentials(HTTP_AUTHORIZATION='')
        self.assertRaises(AssertionError, self.sessions_post)
        self.assertRaises(AssertionError, self.projects_get)
        self.assertRaises(AssertionError, self.projects_tags_get)
        self.assertRaises(AssertionError, self.projects_assets_get)
        self.assertRaises(AssertionError, self.vote_assets_post)
