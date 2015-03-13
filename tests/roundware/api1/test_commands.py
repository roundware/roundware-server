# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import datetime
from urllib import urlencode
import json

from model_mommy import mommy
from mock import patch

from django.test.client import Client
from django.conf import settings
from roundware.rw.models import (ListeningHistoryItem, Asset, Project,
                                 Audiotrack, Session, Vote, Envelope,
                                 Speaker, LocalizedString, MasterUI, UIMapping)
from tests.roundwared.common import (RoundwaredTestCase, FakeRequest,
                                     mock_distance_in_meters_near,
                                     mock_distance_in_meters_far)
from roundware.lib.exception import RoundException
from roundware.api1.commands import (check_for_single_audiotrack, get_asset_info,
                                     get_available_assets)
from roundware.api1 import commands
from roundware.lib import api
from roundware.lib.api import (request_stream, get_project_tags, get_current_streaming_asset,
                               _get_current_streaming_asset, vote_asset)
from roundwared import gpsmixer


def mock_apache_safe_daemon_subprocess(command):
    """ patch this since in tests we cannot allocate memory to subprocess
    """
    return command


def mock_stream_exists(sessionid, audio_format):
    """ patch this since we aren't really testing this yet.
    """
    return True


@patch.object(settings, 'ICECAST_PORT', 8000)
@patch.object(settings, 'ICECAST_HOST', 'rw.com')
@patch.object(settings, 'MEDIA_URL', '/audio/')
@patch.object(api, 'apache_safe_daemon_subprocess',
              mock_apache_safe_daemon_subprocess)
@patch.object(api, 'stream_exists', mock_stream_exists)
class TestServer(RoundwaredTestCase):

    """ test api.py methods
    """

    def setUp(self):
        super(type(self), TestServer).setUp(self)

        self.project1 = mommy.make(Project, name='Uno', recording_radius=10,
                                   id=12, audio_format='ogg',
                                   demo_stream_message_loc=[self.english_msg,
                                                            self.spanish_msg],
                                   out_of_range_url='http://rw.com:8000/outofrange.mp3')
        self.session = mommy.make(Session, project=self.project1,
                                  language=self.spanish, id=1)
        self.asset1 = mommy.make(Asset, project=self.project1, id=1,
                                 audiolength=5000000, volume=0.9,
                                 created=datetime.datetime(
                                     2013, 11, 21, 21, 3, 6, 616402),
                                 latitude='0.1', longitude='0.1',
                                 language=self.english,
                                 tags=(self.tag1,))
        self.asset2 = mommy.make(Asset, project=self.project1, id=2,
                                 language=self.spanish,
                                 tags=(self.tag1,))
        self.envelope1 = mommy.make(Envelope, session=self.session,
                                    assets=[self.asset1, ])
        self.envelope2 = mommy.make(Envelope, session=self.session,
                                    assets=[self.asset2, ])
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

    def test_check_for_single_audiotrack(self):
        self.assertEquals(True, check_for_single_audiotrack(self.session.id))

    def test_get_current_streaming_asset_multi_audiotrack(self):
        """ must raise RoundException if project has more than one AudioTrack
        """
        req = FakeRequest()
        req.GET = {'session_id': self.session.id}
        track2 = mommy.make(Audiotrack, project=self.project1, id=2)
        with self.assertRaises(RoundException):
            current = get_current_streaming_asset(req)
            # delete extra track
            Audiotrack.objects.filter(id__exact=2).delete()

    def test_get_current_streaming_asset(self):

        req = FakeRequest()
        req.GET = {'session_id': self.session.id}
        current = get_current_streaming_asset(req)
        self.assertEquals('dict', type(current).__name__)
        self.assertEquals(2, current['asset_id'])
        self.assertEquals('2013-11-21T17:29:44.610672', current['start_time'])
        self.assertEquals(6, current['duration_in_stream'])
        # don't bother testing current server time here

    def test_get_asset_info(self):
        req = FakeRequest()
        req.GET = {'session_id': self.session.id, 'asset_id': self.asset1.id}
        expected = {"asset_id": 1,
                    "created": '2013-11-21T21:03:06.616402',
                    "duraton_in_ms": 5}
        self.assertEquals(expected, get_asset_info(req))

    def test_play_asset_in_stream(self):
        pass

    def test_skip_ahead(self):
        pass

    def test_vote_asset(self):
        req = FakeRequest()
        req.GET = {'session_id': self.session.id, 'asset_id': 1,
                   'vote_type': 'like', 'value': 2}
        ret = vote_asset(req)
        self.assertEqual(True, ret["success"])
        votes = Vote.objects.filter(asset__id__exact=1)
        self.assertTrue(len(votes) == 1)

    def test_get_config(self):
        pass

    def test_get_tags_for_project(self):
        pass

    # get_available_assets
    # Return JSON serializable dictionary with the number of matching assets
    # by media type and a list of available assets based on filter criteria passed in
    # request.  If asset_id is passed, ignore other filters and return single
    # asset.  If multiple, comma-separated values for asset_id are passed, ignore
    # other filters and return all those assets.  If envelope_id is passed, ignore
    # other filters and return all assets in that envelope.  If multiple,
    # comma-separated values for envelope_id are passed, ignore
    # other filters and return all those assets.  Returns localized
    # value for tag strings on asset by asset basis unless a specific language
    # code is passed. Fall back to English if necessary.

    ASSET_1 = {
        'asset_id': 1,
        'asset_url': '/audio/None',
        'audio_length': 5000000,
        'description': '',
        'language': 'en',
        'latitude': 0.1,
        'loc_description': '',
        'longitude': 0.1,
        'mediatype': 'audio',
        'project': 'Uno',
        'submitted': True,
    }

    ASSET_1_TAGS_EN = {
        'tags': [{
            'tag_category_name': 'tagcatname',
            'tag_id': 1,
            'localized_value': 'One'
        }]
    }

    ASSET_2 = {
        'asset_id': 2,
        'asset_url': '/audio/None',
        'audio_length': None,
        'description': '',
        'language': 'es',
        'latitude': None,
        'loc_description': '',
        'longitude': None,
        'mediatype': 'audio',
        'project': 'Uno',
        'submitted': True,
    }

    ASSET_2_TAGS_EN = ASSET_1_TAGS_EN

    ASSET_1_TAGS_ES = {
        'tags': [{
            'tag_category_name': 'tagcatname',
            'tag_id': 1,
            'localized_value': 'Uno'
        }]
    }

    ASSET_2_TAGS_ES = ASSET_1_TAGS_ES

    def test_get_available_assets_pass_asset_id(self):
        """ ignore other filters and return single asset info
        """
        req = FakeRequest()
        req.GET = {'asset_id': '1', 'project_id': '2', 'tagids': '2,3'}
        expected = {
            'number_of_assets': {
                'audio': 1, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items())]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_pass_multiple_asset_ids(self):
        """ ignore other filters and return assets matching ids passed
        """
        req = FakeRequest()
        req.GET = {'asset_id': '1,2', 'project_id': '2', 'tagids': '2,3'}
        expected = {
            'number_of_assets': {
                'audio': 2, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items()),

                       dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_ES.items()),
                       ]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_func_get_available_assets_pass_multiple_asset_ids_GET(self):
        """ make sure response includes proper JSON using a Client request
        """
        cl = Client()
        op = 'get_available_assets'
        req_dict = {'asset_id': '1,2', 'project_id': '2', 'tagids': '2,3'}
        f_set = urlencode(req_dict)
        req_str = '/api/1/?operation={0}&{1}'.format(op, f_set)
        response = cl.get(req_str)
        self.assertEquals(200, response.status_code)
        js = json.loads(response.content)
        self.assertEqual(2, js['number_of_assets']['audio'])
        self.assertEqual(0, js['number_of_assets']['photo'])
        self.assertEqual(0, js['number_of_assets']['video'])
        self.assertEqual(0, js['number_of_assets']['text'])
        self.assertEqual([dict(self.ASSET_1.items() +
                               self.ASSET_1_TAGS_EN.items()),

                          dict(self.ASSET_2.items() +
                               self.ASSET_2_TAGS_ES.items())], js['assets'])

    def test_func_get_available_assets_pass_multiple_asset_ids_POST(self):
        """ make sure response includes proper JSON using a Client request
        """
        cl = Client()
        req_dict = {'operation': 'get_available_assets',
                    'asset_id': '1,2', 'project_id': '2', 'tagids': '2,3'}
        # f_set = cl.encode_multipart(req_dict)
        response = cl.post('/api/1/', req_dict)
        self.assertEquals(200, response.status_code)
        js = json.loads(response.content)
        self.assertEqual(2, js['number_of_assets']['audio'])
        self.assertEqual(0, js['number_of_assets']['photo'])
        self.assertEqual(0, js['number_of_assets']['video'])
        self.assertEqual(0, js['number_of_assets']['text'])
        self.assertEqual([dict(self.ASSET_1.items() +
                               self.ASSET_1_TAGS_EN.items()),

                          dict(self.ASSET_2.items() +
                               self.ASSET_2_TAGS_ES.items())], js['assets'])

    def test_get_available_assets_pass_an_invalid_asset_id(self):
        """ ignore other filters and return assets matching ids passed.
            ignore invalid asset id.
        """
        req = FakeRequest()
        req.GET = {'asset_id': '1,2,3', 'project_id': '2', 'tagids': '2,3'}
        expected = {
            'number_of_assets': {
                'audio': 2, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items()),

                       dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_ES.items()),
                       ]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_pass_language(self):
        """make sure tag localized messages are returned in passed
           language
        """
        req = FakeRequest()
        req.GET = {'asset_id': '1', 'tagids': '2,3', 'language': 'es'}
        expected = {
            'number_of_assets': {
                'audio': 1, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_ES.items())]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_pass_project_id(self):
        req = FakeRequest()
        req.GET = {'project_id': '12'}
        expected = {
            'number_of_assets': {
                'audio': 2, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items()),

                       dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_ES.items()),
                       ]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_request_language_trumps_asset_language(self):
        """ asset2 is in Spanish.  request for English returns tag
        localized message in English.
        """
        req = FakeRequest()
        req.GET = {'asset_id': '2', 'language': 'en'}
        expected = {
            'number_of_assets': {
                'audio': 1, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_EN.items()),
                       ]
        }
        self.assertEquals(expected, get_available_assets(req))

    @patch.object(gpsmixer, 'distance_in_meters',
                  mock_distance_in_meters_near)
    def test_get_available_assets_pass_lat_long_near(self):
        """ with mocked gpsmixer.distance_in_meters to always return a
        distance of 0 meters, we should get all assets when a latitude
        and longitude are specified
        """
        req = FakeRequest()
        req.GET = {'latitude': '0.1', 'longitude': '0.1', 'project_id': '12'}
        expected = {
            'number_of_assets': {
                'audio': 2, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items()),
                       dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_ES.items())
                       ]
        }
        self.assertEquals(expected, get_available_assets(req))

    @patch.object(gpsmixer, 'distance_in_meters',
                  mock_distance_in_meters_far)
    def test_get_available_assets_pass_lat_long_far(self):
        """ with mocked gpsmixer.distance_in_meters to always return a
        distance of 0 meters, we should get all assets when a latitude
        and longitude are specified
        """
        req = FakeRequest()
        req.GET = {'latitude': '0.1', 'longitude': '0.1', 'project_id': '12'}
        expected = {
            'number_of_assets': {
                'audio': 0, 'photo': 0, 'text': 0, 'video': 0

            },
            'assets': []
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_pass_tag_ids_with_and(self):
        """ test assets returned have both tags if no tagbool of 'or'
            passed.
        """
        req = FakeRequest()
        req.GET = {'tagids': '1,2', 'project_id': '12'}
        expected = {
            'number_of_assets': {
                'audio': 0,
                'photo': 0,
                'text': 0,
                'video': 0
            },
            'assets': []
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_pass_tag_ids_with_or(self):
        """ test assets returned only need match one of passed tags 
        """
        req = FakeRequest()
        req.GET = {'tagids': '1,2', 'project_id': '12', 'tagbool': 'or'}
        expected = {
            'number_of_assets': {
                'audio': 2, 'photo': 0, 'text': 0, 'video': 0

            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items()),
                       dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_ES.items())
                       ]
        }
        self.assertEquals(expected, get_available_assets(req))

    @patch.object(gpsmixer, 'distance_in_meters',
                  mock_distance_in_meters_near)
    def test_get_available_assets_pass_radius(self):
        """project's radius is bigger than the mock near distance.  
        should get no assets if we pass a radius of 0, overriding
        project radius.
        """
        req = FakeRequest()
        req.GET = {'radius': '0', 'project_id': '12',
                   'latitude': '0.1', 'longitude': '0.1'}
        expected = {
            'number_of_assets': {
                'audio': 0, 'photo': 0, 'text': 0, 'video': 0

            },
            'assets': []
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_pass_envelope_id(self):
        """ ignore other filters and return asset info for 
            assets in envelope.
        """
        req = FakeRequest()
        req.GET = {'envelope_id': '1', 'project_id': '2', 'tagids': '2,3'}
        expected = {
            'number_of_assets': {
                'audio': 1, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items())]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_pass_multiple_envelope_ids(self):
        """ ignore other filters and return asset info for 
            assets in envelopes.
        """
        req = FakeRequest()
        req.GET = {'envelope_id': '1,2', 'project_id': '2', 'tagids': '2,3'}
        expected = {
            'number_of_assets': {
                'audio': 2, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items()),
                       dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_ES.items())
                       ]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_pass_bad_envelope(self):
        """ ignore other filters and return asset info for 
            assets in envelopes, ignoring bad envelope id.
        """
        req = FakeRequest()
        req.GET = {'envelope_id': '1,2,3', 'project_id': '2', 'tagids': '2,3'}
        expected = {
            'number_of_assets': {
                'audio': 2, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items()),
                       dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_ES.items())
                       ]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_pass_extra_kwarg(self):
        """ extra kwargs should provide extra filter 
        """
        req = FakeRequest()
        req.GET = {'project_id': '12', 'audiolength': '5000000'}
        expected = {
            'number_of_assets': {
                'audio': 1, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_1.items() +
                            self.ASSET_1_TAGS_EN.items())]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_func_get_available_assets_pass_extra_kwarg(self):
        """ make sure response includes proper JSON using a Client request
        """
        cl = Client()
        op = 'get_available_assets'
        req_dict = {'project_id': '12', 'audiolength': '5000000'}
        f_set = urlencode(req_dict)
        req_str = '/api/1/?operation={0}&{1}'.format(op, f_set)
        response = cl.get(req_str)
        self.assertEquals(200, response.status_code)
        js = json.loads(response.content)
        self.assertEqual(1, js['number_of_assets']['audio'])
        self.assertEqual(0, js['number_of_assets']['photo'])
        self.assertEqual(0, js['number_of_assets']['video'])
        self.assertEqual(0, js['number_of_assets']['text'])
        self.assertEqual([dict(self.ASSET_1.items() +
                               self.ASSET_1_TAGS_EN.items())], js['assets'])

    def test_get_available_assets_pass_extra_kwarg_with_asset_id(self):
        """ extra kwargs should get ignored if we ask for an asset_id
        """
        req = FakeRequest()
        req.GET = {'asset_id': '2', 'audiolength': '5000000'}
        expected = {
            'number_of_assets': {
                'audio': 1, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_ES.items())]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_get_available_assets_invalid_kwarg_does_no_harm(self):
        """ an extra kwarg in request that isn't a field on the Asset model
            doesn't have any effect
        """
        req = FakeRequest()
        req.GET = {'asset_id': '2', 'foo': 'bar'}
        expected = {
            'number_of_assets': {
                'audio': 1, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': [dict(self.ASSET_2.items() +
                            self.ASSET_2_TAGS_ES.items())]
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_func_get_available_invalid_kwarg_does_no_harm(self):
        """ make sure response includes proper JSON using a Client request
        """
        cl = Client()
        op = 'get_available_assets'
        req_dict = {'asset_id': '2', 'foo': 'bar'}
        f_set = urlencode(req_dict)
        req_str = '/api/1/?operation={0}&{1}'.format(op, f_set)
        response = cl.get(req_str)
        self.assertEquals(200, response.status_code)
        js = json.loads(response.content)
        self.assertEqual(1, js['number_of_assets']['audio'])
        self.assertEqual(0, js['number_of_assets']['photo'])
        self.assertEqual(0, js['number_of_assets']['video'])
        self.assertEqual(0, js['number_of_assets']['text'])
        self.assertEqual([dict(self.ASSET_2.items() +
                               self.ASSET_2_TAGS_ES.items())], js['assets'])

    def test_get_available_assets_kwargs_must_all_be_satisfied(self):
        """ assets returned must match all valid kwargs passed
        """
        req = FakeRequest()
        req.GET = {'project_id': '12', 'audiolength': '5000000',
                   'volume': '1.0'}
        expected = {
            'number_of_assets': {
                'audio': 0, 'photo': 0, 'text': 0, 'video': 0
            },
            'assets': []
        }
        self.assertEquals(expected, get_available_assets(req))

    def test_func_get_available_assets_kwargs_must_all_be_satisfied(self):
        """ make sure response includes proper JSON using a Client request
        """
        cl = Client()
        op = 'get_available_assets'
        req_dict = {'project_id': '12', 'audiolength': '5000000',
                    'volume': '1.0', }
        f_set = urlencode(req_dict)
        req_str = '/api/1/?operation={0}&{1}'.format(op, f_set)
        response = cl.get(req_str)
        self.assertEquals(200, response.status_code)
        js = json.loads(response.content)
        self.assertEqual(0, js['number_of_assets']['audio'])
        self.assertEqual(0, js['number_of_assets']['photo'])
        self.assertEqual(0, js['number_of_assets']['video'])
        self.assertEqual(0, js['number_of_assets']['text'])
        self.assertEqual([], js['assets'])

    ################
    # request_stream
    ################

    def test_request_stream_demo_stream_enabled(self):
        """ Make sure we get the demo stream data if it's enabled for the 
        session, and the localized message in the correct language for the 
        session. Doesn't test actual stream being served.
        """
        req = FakeRequest()
        req.GET = {'session_id': '1'}
        self.session.demo_stream_enabled = True
        self.session.save()
        expected = {
            'stream_url': 'http://rw.com:8000/demo_stream.mp3',
            'demo_stream_message': 'Uno'
        }
        self.assertEquals(expected, request_stream(req))
        self.session.demo_stream_enabled = False
        self.session.save()

    @patch.object(gpsmixer, 'distance_in_meters',
                  mock_distance_in_meters_near)
    def test_request_stream_listener_in_range(self):
        """ Make sure we get good stream data if listener is in range.
        Doesn't test actual stream being served.
        """
        req = FakeRequest()
        req.GET = {'session_id': '1', 'latitude': '0.1', 'longitude': '0.1'}
        expected = {'stream_url': 'http://rw.com:8000/stream1.ogg'}
        self.assertEquals(expected, request_stream(req))

    @patch.object(gpsmixer, 'distance_in_meters',
                  mock_distance_in_meters_near)
    def test_request_stream_listener_in_range_no_lat_long_passed(self):
        """ Make sure we get good stream data if no lat/long passed
        Doesn't test actual stream being served.
        """
        req = FakeRequest()
        req.GET = {'session_id': '1'}
        expected = {'stream_url': 'http://rw.com:8000/stream1.ogg'}
        self.assertEquals(expected, request_stream(req))

    @patch.object(gpsmixer, 'distance_in_meters', mock_distance_in_meters_far)
    def test_request_stream_listener_out_of_range(self):
        """ Make sure we get out of range message if listener is too far.
        Doesn't test actual stream being served.
        """
        req = FakeRequest()
        req.GET = {'session_id': '1', 'latitude': '0.1', 'longitude': '0.1'}
        expected = {
            'user_message': ('This application is designed to be used in '
                             'specific geographic locations. Apparently '
                             'your phone thinks you are not at one of those '
                             'locations, so you will hear a sample audio '
                             'stream instead of the real deal. If you think '
                             'your phone is incorrect, please restart Scapes '
                             'and it will probably work. Thanks for '
                             'checking it out!'),
            'stream_url': 'http://rw.com:8000/outofrange.mp3'}
        self.assertEquals(expected, request_stream(req))

    @patch.object(gpsmixer, 'distance_in_meters', mock_distance_in_meters_near)
    def test_request_stream_inactive_speakers_not_involved(self):
        """ Inactive speakers don't count for in-range
        """
        req = FakeRequest()
        req.GET = {'session_id': '1', 'latitude': '0.1', 'longitude': '0.1'}
        self.speaker1.activeyn = False
        self.speaker1.save()
        expected = {
            'user_message': ('This application is designed to be used in '
                             'specific geographic locations. Apparently '
                             'your phone thinks you are not at one of those '
                             'locations, so you will hear a sample audio '
                             'stream instead of the real deal. If you think '
                             'your phone is incorrect, please restart Scapes '
                             'and it will probably work. Thanks for '
                             'checking it out!'),
            'stream_url': 'http://rw.com:8000/outofrange.mp3'}
        self.assertEquals(expected, request_stream(req))
        self.speaker1.activeyn = True
        self.speaker1.save()

    @patch.object(gpsmixer, 'distance_in_meters', mock_distance_in_meters_far)
    def test_request_stream_just_one_speaker_in_range_needed(self):
        speaker2 = mommy.make(Speaker, project=self.project1,
                              latitude=0.1, longitude=0.1,
                              maxdistance=2000000000000, activeyn=True)
        speaker2.save()
        req = FakeRequest()
        req.GET = {'session_id': '1'}
        expected = {'stream_url': 'http://rw.com:8000/stream1.ogg'}
        self.assertEquals(expected, request_stream(req))

    @patch.object(gpsmixer, 'distance_in_meters', mock_distance_in_meters_far)
    def test_project_out_of_range_message_localized(self):
        pass


class TestGetProjectTagJSON(RoundwaredTestCase):
    """ test various permutations of api.get_config_tag
    """
    def setUp(self):
        super(type(self), TestGetProjectTagJSON).setUp(self)

        # make a masterui, a project, a ui_mode, tag category, selectionmethod
        self.english_hdr = mommy.make(LocalizedString,
                                      localized_string="Head",
                                      language=self.english)
        self.spanish_hdr = mommy.make(LocalizedString,
                                      localized_string="Cabeza",
                                      language=self.spanish)
        self.masterui = mommy.make(MasterUI, active=True,
                                   ui_mode=MasterUI.LISTEN, index=1,
                                   tag_category__name='TagCatName',
                                   header_text_loc=[self.english_hdr,
                                                    self.spanish_hdr])
        self.ui_mode_one = self.masterui.ui_mode

        self.english_sess = mommy.make(Session, project=self.masterui.project,
                                       language=self.english)
        self.spanish_sess = mommy.make(Session, project=self.masterui.project,
                                       language=self.spanish)
        self.project_one = self.masterui.project
        self.ui_mapping_one = mommy.make(UIMapping, master_ui=self.masterui,
                                         active=True, tag=self.tag1,
                                         index=1, default=True)
        self.master_ui_two = mommy.make(MasterUI, name='inactivemui',
                                        ui_mode=self.ui_mode_one, active=True)
        self.project_two = self.master_ui_two.project
        self.project_three = mommy.make(Project, name='project_three')

    def _proj_one_config(self):
        # Translate the description tag like db.get_config_tag_json()
        loc_desc = ""
        temp_desc = self.ui_mapping_one.tag.loc_description.filter(language=self.english)
        if temp_desc:
            loc_desc = temp_desc[0].localized_string

        return {'listen': [
            {'name': self.masterui.name,
             'header_text': "Head",
             'code': 'TagCatName',
             'select': self.masterui.get_select_display(),
             'order': 1,
             'defaults': [self.ui_mapping_one.tag.id],
             'options': [{
                 'tag_id': self.ui_mapping_one.tag.id,
                 'order': 1,
                 'data': "{'json':'value'}",
                 'description': self.ui_mapping_one.tag.description,
                 'loc_description': loc_desc,
                 'shortcode': self.ui_mapping_one.tag.value,
                 'relationships': [],
                 'value': 'One'
             }]},
        ]}

    def test_get_uimapping_info_for_project(self):
        """ Test proper UIMapping data returned based on project passed """
        config = get_project_tags(self.project_one, self.english_sess)
        expected = self._proj_one_config()
        self.assertEquals(expected, config)

    def test_only_masteruis_for_project_returned(self):
        """ Confirm only info for MasterUIs for passed project or session
            project are returned in config tag dictionary
        """
        config = get_project_tags(self.project_three)
        self.assertEquals({}, config)

        config = get_project_tags(self.project_two)
        # should not have any uimapping info for project _one_
        self.assertNotIn(self.masterui.name,
                         [dic['name'] for dic in
                          config['listen']])

    def test_session_project_overrides_passed_project(self):
        """ The project associated with a passed session should be used 
            even if a project is explicitly passed. (really?)
        """
        pass

    def test_only_active_masteruis_returned(self):
        """ Confirm that only active MasterUIs are returned in 
            config tag 'JSON' (dictionary)
        """
        self.master_ui_two.active = False
        self.master_ui_two.save()
        config = get_project_tags(self.project_two)
        self.assertEquals({}, config)
        self.master_ui_two.active = True
        self.master_ui_two.save()

    def test_get_right_masterui_without_passed_project(self):
        """ Don't pass a project, just use the project for the session.
            Do we still get the right MasterUI?
        """
        config = get_project_tags(None, self.english_sess)
        expected = self._proj_one_config()
        self.assertEquals(expected, config)

    def test_get_correct_localized_header_text(self):
        """ Test that we get correct localized header text for session, or if 
            none passed, header text in English.
        """
        config = get_project_tags(None, self.spanish_sess)
        self.assertEquals('Cabeza',
                          config['listen'][0]['header_text'])

    def test_tag_values_correctly_localized(self):
        """ Test that we get correct localized text for tag values
            based on session language, or if none passed, in English.
        """
        config = get_project_tags(None, self.spanish_sess)
        self.assertEquals('Uno',
                          config['listen'][0]['options'][0]['value'])


class TestListeningHistoryDB(RoundwaredTestCase):

    def setUp(self):
        super(type(self), TestListeningHistoryDB).setUp(self)

        self.project1 = mommy.make(Project)
        self.asset1 = mommy.make(Asset, project=self.project1)
        self.asset2 = mommy.make(Asset, project=self.project1)
        self.history1 = mommy.make(ListeningHistoryItem, asset=self.asset1,
                                   session=self.default_session,
                                   starttime=datetime.datetime.now())
        self.history2 = mommy.make(ListeningHistoryItem, asset=self.asset2,
                                   session=self.default_session,
                                   starttime=datetime.datetime.now())

    def test_get_current_streaming_asset(self):
        self.assertEquals(self.history2, _get_current_streaming_asset(
                          self.default_session.id))
