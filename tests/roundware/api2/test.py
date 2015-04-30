# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.


from __future__ import unicode_literals
import datetime

from model_mommy import mommy
from model_mommy.generators import gen_file_field

from django.conf import settings
from django.core.urlresolvers import reverse

from roundware.rw.models import (ListeningHistoryItem, Asset, Project,
                                 Audiotrack, Session, Envelope,
                                 Speaker, LocalizedString, MasterUI, UIMapping,
                                 Language, Tag, TagCategory)
from roundware.settings import DEFAULT_SESSION_ID

from rest_framework import status
from rest_framework.test import APITestCase


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
        self.default_session = mommy.make(Session, id=DEFAULT_SESSION_ID)
        self.english = mommy.make(Language, language_code='en')
        self.spanish = mommy.make(Language, language_code='es')
        self.english_msg = mommy.make(LocalizedString, localized_string="One",
                                      language=self.english)
        self.spanish_msg = mommy.make(LocalizedString, localized_string="Uno",
                                      language=self.spanish)
        # create project and session
        self.project1 = mommy.make(Project, name='Uno', recording_radius=10,
                                   id=1, audio_format='ogg',
                                   demo_stream_message_loc=[self.english_msg,
                                                            self.spanish_msg],
                                   out_of_range_url='http://rw.com:8000/outofrange.mp3')
        self.session = mommy.make(Session, project=self.project1,
                                  language=self.english, id=1)
        # setup tags
        self.tagcat1 = mommy.make(TagCategory, name='tagcatname')
        self.tagcat2 = mommy.make(TagCategory)
        self.tagcat3 = mommy.make(TagCategory)
        self.tag1 = mommy.make(Tag, data="{'json':'value'}",
                               loc_msg=[self.english_msg, self.spanish_msg],
                               tag_category=self.tagcat1,
                               value='tag1', id=1)
        self.tag2 = mommy.make(Tag, tag_category=self.tagcat2, value='tag2')
        self.tag3 = mommy.make(Tag, tag_category=self.tagcat3, value='tag3')
        self.masterui1 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=MasterUI.LISTEN,
                                    tag_category=self.tagcat1)
        self.masterui2 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=MasterUI.LISTEN,
                                    tag_category=self.tagcat2)
        self.masterui3 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=MasterUI.SPEAK,
                                    tag_category=self.tagcat1)
        self.masterui4 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=MasterUI.SPEAK,
                                    tag_category=self.tagcat2)
        self.masterui5 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=MasterUI.SPEAK,
                                    tag_category=self.tagcat3)
        self.uimapping1 = mommy.make(UIMapping, master_ui=self.masterui1,
                                     tag=self.tag1, active=True)
        self.uimapping2 = mommy.make(UIMapping, master_ui=self.masterui1,
                                     tag=self.tag2, active=True)
        # setup assets and envelopes
        self.asset1 = mommy.make(Asset, project=self.project1, id=1,
                                 audiolength=5000000, volume=0.9,
                                 created=datetime.datetime(
                                     2013, 11, 21, 21, 3, 6, 616402),
                                 latitude='0.1', longitude='0.1',
                                 language=self.english,
                                 tags=(self.tag1,))
        self.asset2 = mommy.make(Asset, project=self.project1, id=2,
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
                                   latitude=0.1, longitude=0.1,
                                   maxdistance=2, activeyn=True)

    def test_api2_in_order(self):
        self.users_post()
        self.sessions_post()
        self.projects_get()
        self.projects_tags_get()
        self.projects_assets_get()

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
        data = {"timezone": "-0500",
                "project_id": 1,
                "client_system": "iOS"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # language wasn't provided, so should be set default to "en"
        self.assertEqual(response.data["language"], "en")
        # check returned data matches data provided
        self.assertEqual(response.data["timezone"], data["timezone"])
        self.assertEqual(response.data["client_system"], data["client_system"])
        self.assertEqual(response.data["project_id"], data["project_id"])
        self.assertIsNotNone(response.data["session_id"])
        # save session_id for later requests
        self.session_id = response.data["session_id"]

    def projects_get(self):
        url = "%s?session_id=%s" % (reverse('project-detail', args=[1]), self.session_id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ensure _loc fields are transformed
        self.assertIn("out_of_range_message", response.data)
        self.assertNotIn("out_of_range_message_loc", response.data)
        self.assertEqual(1, response.data["project_id"])

    def projects_tags_get(self):
        url = "%s?session_id=%s" % (reverse('project-tags', args=[1]), self.session_id)
        data = {}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(response.data["speak"]), 3)
        self.assertEqual(len(response.data["listen"]), 2)
        self.assertEqual(len(response.data["listen"][0]["options"]), 2)

    def projects_assets_get(self):
        url = reverse('project-assets', args=[1])
        data = {}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["project"], 1)

    def ensure_token_required(self):
        self.client.credentials(HTTP_AUTHORIZATION='')
        self.assertRaises(AssertionError, self.sessions_post)
        self.assertRaises(AssertionError, self.projects_get)
        self.assertRaises(AssertionError, self.projects_tags_get)
        self.assertRaises(AssertionError, self.projects_assets_get)
