from __future__ import unicode_literals
import datetime
from urllib import urlencode
import json

from model_mommy import mommy
from mock import patch

from django.test.client import Client

from .common import (RoundwaredTestCase, FakeRequest,
                     mock_distance_in_meters_near,
                     mock_distance_in_meters_far)
from roundware.rw.models import (ListeningHistoryItem, Asset, Project,
                                 Audiotrack, Session, Vote, Envelope,
                                 Speaker)
from roundwared.roundexception import RoundException
from roundwared.server import (check_for_single_audiotrack, get_asset_info,
                               get_current_streaming_asset,
                               get_available_assets,
                               vote_asset, request_stream)
from roundwared import server
from roundwared import gpsmixer
from django.conf import settings


def mock_apache_safe_daemon_subprocess(command):
    """ patch this since in tests we cannot allocate memory to subprocess
    """
    return command


def mock_wait_for_stream(sessionid, audio_format):
    """ patch this since we aren't really testing this yet.
    """
    return {'sessionid': sessionid, 'audio_format': audio_format}


@patch.object(settings, 'ICECAST_PORT', 8000)
@patch.object(settings, 'EXTERNAL_HOST_NAME_WITHOUT_PORT', 'rw.com')
@patch.object(settings, 'ICECAST_HOST', 'rw.com')
@patch.object(server, 'apache_safe_daemon_subprocess',
              mock_apache_safe_daemon_subprocess)
@patch.object(server, 'wait_for_stream', mock_wait_for_stream)
@patch.object(settings, 'AUDIO_FILE_URI', '/audio/')
class TestServer(RoundwaredTestCase):

    """ test server.py methods
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
        self.assertEqual({"success": True}, vote_asset(req))
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
        'latitude': 0.1,
        'longitude': 0.1,
        'audio_length': 5000000,
        'submitted': True,
        'project': u'Uno',
        'language': u'en',
    }

    ASSET_1_TAGS_EN = {
        'tags': [{
            'tag_category_name': u'tagcatname',
            'tag_id': 1,
            'localized_value': u'One'
        }]
    }

    ASSET_2 = {
        'asset_id': 2,
        'asset_url': '/audio/None',
        'latitude': None,
        'longitude': None,
        'audio_length': None,
        'submitted': True,
        'project': u'Uno',
        'language': u'es',
    }

    ASSET_2_TAGS_EN = ASSET_1_TAGS_EN

    ASSET_1_TAGS_ES = {
        'tags': [{
            'tag_category_name': u'tagcatname',
            'tag_id': 1,
            'localized_value': u'Uno'
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
        req_str = '/roundware?operation={0}&{1}'.format(op, f_set)
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
        op = 'get_available_assets'
        req_dict = {'operation': 'get_available_assets',
                    'asset_id': '1,2', 'project_id': '2', 'tagids': '2,3'}
        # f_set = cl.encode_multipart(req_dict)
        response = cl.post('/roundware/', req_dict)
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
                'audio': 0, 'photo': 0, 'text': 0, 'video': 0

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
        req_str = '/roundware?operation={0}&{1}'.format(op, f_set)
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
        req_str = '/roundware?operation={0}&{1}'.format(op, f_set)
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
        req_str = '/roundware?operation={0}&{1}'.format(op, f_set)
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
                             'specific geographic locations.  Apparently '
                             'your phone thinks you are not at one of those '
                             'locations, so you will hear a sample audio '
                             'stream instead of the real deal.  If you think '
                             'your phone is incorrect, please restart Scapes '
                             'and it will probably work.  Thanks for '
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
                             'specific geographic locations.  Apparently '
                             'your phone thinks you are not at one of those '
                             'locations, so you will hear a sample audio '
                             'stream instead of the real deal.  If you think '
                             'your phone is incorrect, please restart Scapes '
                             'and it will probably work.  Thanks for '
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
