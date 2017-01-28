# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from model_mommy import mommy
from mock import patch

from .common import mock_distance_in_meters_near
from roundware.rw.models import (Session, Asset, Language, LocalizedString, Audiotrack,
                                 Project, UIGroup, UIItem, Tag, TagCategory, TimedAsset)
from roundwared.recording_collection import RecordingCollection
from roundwared.stream import RoundStream
from roundwared import gpsmixer
from roundwared import asset_sorters
from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework import status
from time import sleep

from rest_framework.test import APITestCase


settings.DEBUG = True


class TestRecordingCollection(APITestCase):

    """ Exercise methods and instances of RecordingCollection
    """

    def setUp(self):
        super(type(self), TestRecordingCollection).setUp(self)

        self.default_session = mommy.make(Session)
        self.english = mommy.make(Language, language_code='en', id=1)
        self.spanish = mommy.make(Language, language_code='es', id=2)
        self.english_msg = mommy.make(LocalizedString, localized_string="One",
                                      language=self.english)
        self.spanish_msg = mommy.make(LocalizedString, localized_string="Uno",
                                      language=self.spanish)
        self.tagcat1 = mommy.make(TagCategory, name='tagcatname')
        self.tag1 = mommy.make(Tag, data="{'json':'value'}",
                               loc_msg=[self.english_msg, self.spanish_msg],
                               tag_category=self.tagcat1,
                               value='tag1', id=1)

        self.project1 = mommy.make(Project, name='Project One',
                                   recording_radius=10,
                                   repeat_mode=Project.STOP,
                                   geo_listen_enabled=True)
        self.project2 = mommy.make(Project, name='Project Two',
                                   recording_radius=20,
                                   geo_listen_enabled=True)
        self.project3 = mommy.make(Project, name='Project Three',
                                   recording_radius=10,
                                   repeat_mode=Project.STOP,
                                   geo_listen_enabled=True,
                                   timed_asset_priority=True)
        self.session1 = mommy.make(Session, project=self.project1,
                                   language=self.english)
        self.session2 = mommy.make(Session, project=self.project2,
                                   language=self.english)
        self.session3 = mommy.make(Session, project=self.project3,
                                   language=self.english)
        self.session4 = mommy.make(Session, project=self.project1,
                                   language=self.english, device_id="123456")
        # A new tag only for asset #3.
        self.tag2 = mommy.make(Tag, data="{'json':'value'}",
                               loc_msg=[self.english_msg, self.spanish_msg],
                               tag_category=self.tagcat1,
                               value='tag2', id=2)
        self.req1 = {"session_id": self.session1.id,
                     "project_id": self.project1.id,
                     "audio_stream_bitrate": '128',
                     "latitude": 0.1, "longitude": 0.1}
        self.req2 = {"session_id": self.session1.id,
                     "project_id": self.project1.id,
                     "audio_stream_bitrate": '128'}
        self.req3 = {"session_id": self.session3.id,
                     "project_id": self.project3.id,
                     "audio_stream_bitrate": '128',
                     "latitude": 0.1, "longitude": 0.1}
        self.asset1 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag1],
                                 audiolength=2000,
                                 latitude=0.1, longitude=0.1)
        self.asset2 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag1],
                                 audiolength=2000, weight=100,
                                 latitude=0.1, longitude=0.1)
        self.asset3 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag2],
                                 audiolength=2000, weight=200,
                                 latitude=0.1, longitude=0.1)
        self.asset4 = mommy.make(Asset, project=self.project3,
                                 language=self.english,
                                 tags=[self.tag2],
                                 audiolength=2000, weight=50,
                                 latitude=2, longitude=2)
        self.asset5 = mommy.make(Asset, project=self.project3,
                                 language=self.english,
                                 tags=[self.tag2],
                                 audiolength=2000, weight=200,
                                 latitude=0.1, longitude=0.1)
        self.asset6 = mommy.make(Asset, project=self.project3,
                                 language=self.english,
                                 tags=[self.tag1],
                                 audiolength=2000, weight=300,
                                 latitude=0.1, longitude=0.1)
        self.asset7 = mommy.make(Asset, project=self.project3,
                                 language=self.english,
                                 tags=[self.tag2],
                                 audiolength=2000, weight=100,
                                 latitude=2.0, longitude=2.0)
        self.uigroup1 = mommy.make(UIGroup, project=self.project1,
                                    ui_mode=UIGroup.LISTEN,
                                    tag_category=self.tagcat1)
        self.uigroup2 = mommy.make(UIGroup, project=self.project1,
                                    ui_mode=UIGroup.LISTEN,
                                    tag_category=self.tagcat1)
        self.uigroup3 = mommy.make(UIGroup, project=self.project3,
                                    ui_mode=UIGroup.LISTEN,
                                    tag_category=self.tagcat1)
        self.uiitem1 = mommy.make(UIItem, ui_group=self.uigroup1,
                                     tag=self.tag1, default=True, active=True)
        self.uiitem2 = mommy.make(UIItem, ui_group=self.uigroup1,
                                     tag=self.tag2, default=True, active=True)
        self.uiitem3 = mommy.make(UIItem, ui_group=self.uigroup3,
                                     tag=self.tag2, default=True, active=True)
        self.timedasset1 = mommy.make(TimedAsset, project=self.project3,
                                      asset=self.asset4, start=0, end=15)
        self.timedasset2 = mommy.make(TimedAsset, project=self.project3,
                                      asset=self.asset6, start=0, end=30)
        self.timedasset3 = mommy.make(TimedAsset, project=self.project3,
                                      asset=self.asset7, start=0, end=30)
        self.track1 = mommy.make(Audiotrack, project=self.project1, id=1)


    def test_instantiate_recording_collection(self):
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius)
        self.assertEquals(rc.__class__.__name__, 'RecordingCollection')
        self.assertEquals('random', rc.ordering)

    def test_correct_all_recordings(self):
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius)
        self.assertEquals([self.asset1, self.asset2, self.asset3], rc.all)

    def test_update_request_all_recordings_changes(self):
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius)
        req['session_id'] = self.session2.id
        rc.update_request(req)
        self.assertEquals([], rc.all)

    def test_update_nearby_recordings_by_random(self):
        """ test that we don't get the same order more than 8 out of
        10 tests.... not that scientific but probably reasonable
        """
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius)
            order1 = self.asset1
            matched = 0
            for i in range(10):
                rc._update_playlist_proximity(req)
                nearby = rc.get_recording()
                if nearby == order1:
                    matched += 1
            self.assertTrue(matched <= 8)
            self.assertTrue(matched > 0)

    def test_order_assets_by_like(self):
        """
        Order of assets returned should be determined by number of likes.
        List is reverse order because assets are popped off the stack.
        """
        vote1 = mommy.make('rw.Vote', session=self.session1,
                           asset=self.asset2, type="like")
        vote2 = mommy.make('rw.Vote', session=self.session1,
                           asset=self.asset2, type="like")
        vote3 = mommy.make('rw.Vote', session=self.session1,
                           asset=self.asset1, type="like")
        # Use all three votes to stop unuse warnings
        vote1, vote2, vote3
        self.assertEquals([self.asset1, self.asset2],
                          asset_sorters.order_assets_by_like([self.asset1,
                                                              self.asset2]))

    def test_order_assets_by_weight(self):
        """
        Order of assets returned should be determined by asset weight
        List is reverse order because assets are popped off the stack.
        """
        self.assertEquals([self.asset1, self.asset2],
                          asset_sorters.order_assets_by_weight([self.asset1,
                                                               self.asset2]))

    def test_get_recording_until_none_repeatmode_stop(self):
        """
        test that we get the next playlist_proximity nearby recording, until there
        are none left. project in stop repeatmode should then not
        return any recordings.
        """
        req = self.req1
        req["project_id"] = self.project1.id  # required by get_recording
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
            # Update the list of nearby recordings
            rc.update_request(req)

            self.assertEquals(self.asset3, rc.get_recording())
            self.assertEquals(self.asset2, rc.get_recording())
            self.assertEquals(self.asset1, rc.get_recording())
            self.assertIsNone(rc.get_recording())

    def test_get_recording_until_none_then_move(self):
        """ test that we get the next playlist_proximity nearby recording, until there
        are none left. Then move away and back again. Wait for the ban time out
        and they should be available.
        """
        req = self.req1
        # required by get_recording
        req["project_id"] = self.project1.id
        stream = RoundStream(self.session1.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
        # Update the list of nearby recordings
        rc.update_request(req)
        # Listen to the three nearby
        self.assertEquals(self.asset3, rc.get_recording())
        self.assertEquals(self.asset2, rc.get_recording())
        self.assertEquals(self.asset1, rc.get_recording())
        # Check there is nothing left
        self.assertIsNone(rc.get_recording())
        # Move away
        req['latitude'] = 2
        rc.move_listener(req)
        # Check for nothing
        self.assertIsNone(rc.get_recording())
        # Wait for the BANNED_TIMEOUT_LIMIT to NOT pass
        sleep(1)
        # Move back
        req['latitude'] = 0.1
        rc.move_listener(req)
        # Check the assets remain not available.
        self.assertIsNone(rc.get_recording())
        # Wait for the BANNED_TIMEOUT_LIMIT to pass
        sleep(3)
        # re-trigger playlist population
        rc.move_listener(req)
        # Check the assets are available again.
        self.assertEquals(self.asset3, rc.get_recording())
        self.assertEquals(self.asset2, rc.get_recording())
        self.assertEquals(self.asset1, rc.get_recording())

    def test_global_listen_add_and_re_add_to_playlist(self):
        """
        test for global listen projects that all assets are added
        to playlist initially and then re-added with tag filtering
        only after BANNED_TIMEOUT_LIMIT has passed
        """
        self.project1.geo_listen_enabled = False
        self.project1.save()
        req = self.req2
        # required by get_recording
        req["project_id"] = self.project1.id
        stream = RoundStream(self.session1.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
        # Update the list of nearby recordings
        rc.update_request(req)
        # Listen to the three nearby
        self.assertEquals(self.asset3, rc.get_recording())
        self.assertEquals(self.asset2, rc.get_recording())
        self.assertEquals(self.asset1, rc.get_recording())
        # Check there is nothing left
        self.assertIsNone(rc.get_recording())
        # Filter with tags
        req['tags'] = str(self.tag1.id)
        rc.update_request(req)
        # Check for nothing because BANNED_TIMEOUT_LIMIT not passed
        self.assertIsNone(rc.get_recording())
        # Wait for the BANNED_TIMEOUT_LIMIT to pass
        sleep(3)
        # re-trigger playlist population with tag filtering
        rc.update_request(req)
        # Check the filtered assets are available again.
        self.assertEquals(self.asset2, rc.get_recording())
        self.assertEquals(self.asset1, rc.get_recording())

        self.project1.geo_listen_enabled = True
        self.project1.save()

    def test_get_recording_until_none_repeatmode_continuous(self):
        """ test that we get the next playlist_proximity nearby recording, until there
        are none left.  project in continuous repeatmode should then the
        first played recording.
        """
        self.project1.repeat_mode = Project.CONTINUOUS
        self.project1.save()
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
            # Update the list of nearby recordings
            rc.update_request(req)

            self.assertEquals(self.asset3, rc.get_recording())
            self.assertEquals(self.asset2, rc.get_recording())
            self.assertEquals(self.asset1, rc.get_recording())
            # wait for BANNED_TIMEOUT_LIMIT to pass
            sleep(3)
            self.assertEquals(self.asset3, rc.get_recording())

    def test_get_recording_continuous_global_outofrange(self):
        """
        Test that we get the next playlist recording until there are none
        left (out of range of active speakers). Global listen project in
        continuous repeat mode should then replay the first played recording.
        """
        self.project1.repeat_mode = Project.CONTINUOUS
        self.project1.geo_listen_enabled = False
        self.project1.save()
        req = self.req1
        req['latitude'] = 10
        req['longitude'] = 10
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
            # Update the list of nearby recordings
            rc.update_request(req)

            self.assertEquals(self.asset3, rc.get_recording())
            self.assertEquals(self.asset2, rc.get_recording())
            self.assertEquals(self.asset1, rc.get_recording())
            # wait for BANNED_TIMEOUT_LIMIT to pass
            sleep(3)
            self.assertEquals(self.asset3, rc.get_recording())

        self.project1.geo_listen_enabled = True
        self.project1.save()

    def test_get_recording_continuous_global_inrange(self):
        """
        Test that we get the next playlist recording until there are none
        left (in range of active speaker). Global listen project in continuous
        repeat mode should then replay the first played recording.
        """
        self.project1.repeat_mode = Project.CONTINUOUS
        self.project1.geo_listen_enabled = False
        self.project1.save()
        req = self.req1
        req['latitude'] = .1
        req['longitude'] = .1
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
            # Update the list of nearby recordings
            rc.update_request(req)

            self.assertEquals(self.asset3, rc.get_recording())
            self.assertEquals(self.asset2, rc.get_recording())
            self.assertEquals(self.asset1, rc.get_recording())
            # wait for BANNED_TIMEOUT_LIMIT to pass
            sleep(3)
            self.assertEquals(self.asset3, rc.get_recording())

        self.project1.geo_listen_enabled = True
        self.project1.save()

    def test_add_recording(self):
        """ add a specific asset id and it should show up in
        playlist_proximity
        """
        # Request #2 has no lat/long to test that code
        req = self.req2
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius, 'by_like')
            # Update the list of nearby recordings
            rc.update_request(req)
            self.assertEquals([self.asset1, self.asset2, self.asset3],
                              rc.playlist_proximity)
            rc.add_asset_to_rc(self.asset2)
            self.assertEquals([self.asset1, self.asset2, self.asset3,
                               self.asset2], rc.playlist_proximity)

    def test_limit_asset_by_tag(self):
        """ test that only tag1 assets are returned when request["tags"] is specified.
        """
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius, 'by_weight')

            # Return assets with tag1.
            req['tags'] = str(self.tag1.id)
            rc.update_request(req)

            self.assertEquals(self.asset2, rc.get_recording())
            self.assertEquals(self.asset1, rc.get_recording())

            # Return all assets, tests comma detection.
            req['tags'] = "%s,%s" % (self.tag1.id, self.tag2.id)

            rc.update_request(req)
            self.assertEquals(self.asset3, rc.get_recording())
            # Only Asset3 returned because others are banned.
            self.assertEquals(None, rc.get_recording())

    def test_get_recording_geo_listen(self):
        """ Disable geo-listen and confirm all recordings are available.
            Enable geo-listen and confirm no recordings are available.
        """
        self.project1.geo_listen_enabled = False
        self.project1.save()
        req = self.req2
        stream = RoundStream(self.session1.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius, 'by_weight')

        self.assertEquals(self.asset3, rc.get_recording())
        self.assertEquals(self.asset2, rc.get_recording())
        self.assertEquals(self.asset1, rc.get_recording())

        self.project1.geo_listen_enabled = True
        self.project1.save()
        stream = RoundStream(self.session1.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius, 'by_weight')

        self.assertEquals(None, rc.get_recording())

    def test_timed_asset_priority_true(self):
        """ Test that _get_recording returns a proximity asset instead of a
            timed asset when project.timed_asset_priority=True.
        """
        stream = RoundStream(self.session3.id, 'ogg', self.req3)
        rc = RecordingCollection(stream, self.req3, stream.radius, 'by_weight')
        # Force/Fake start the RC timer; needed for timed asset selection
        rc.start()
        # Update the list of nearby recordings
        rc.update_request(self.req3)
        self.assertEquals(self.asset7, rc.get_recording())
        self.assertEquals(self.asset4, rc.get_recording())
        self.assertEquals(self.asset5, rc.get_recording())

    def test_timed_asset_priority_false(self):
        """ Test that _get_recording returns a proximity asset instead of a
            timed asset when project.timed_asset_priority=False.
        """
        self.project3.timed_asset_priority = False
        self.project3.save()
        stream = RoundStream(self.session3.id, 'ogg', self.req3)

        rc = RecordingCollection(stream, self.req3, stream.radius, 'by_weight')
        # Force/Fake start the RC timer; needed for timed asset selection
        rc.start()
        # Update the list of nearby recordings
        rc.update_request(self.req3)
        self.assertEquals(self.asset5, rc.get_recording())
        self.assertEquals(self.asset7, rc.get_recording())
        self.assertEquals(self.asset4, rc.get_recording())

    def test_timed_assets_filtered_by_tags(self):
        """ Setup stream with no location assets and two timed assets.
            Make sure only timed asset with proper tag is returned.
        """
        stream = RoundStream(self.session3.id, 'ogg', self.req3)
        rc = RecordingCollection(stream, self.req3, stream.radius, 'by_weight')
        # Force/Fake start the RC timer; needed for timed asset selection
        rc.start()
        # Return assets with tag1.
        self.req3['tags'] = str(self.tag1.id)
        # move to location with no assets
        self.req3['latitude'] = 0
        # Update the list of nearby recordings
        rc.update_request(self.req3)
        self.assertEquals(self.asset6, rc.get_recording())
        self.assertEquals(None, rc.get_recording())

    def test_timed_asset_ordering_by_weight(self):
        """ Test that timed assets are ordered per the project.ordering
            parameter (in this case 'by_weight').
        """
        stream = RoundStream(self.session3.id, 'ogg', self.req3)
        rc = RecordingCollection(stream, self.req3, stream.radius, 'by_weight')
        # Force/Fake start the RC timer; needed for timed asset selection
        rc.start()
        # move to location with no geo-assets
        self.req3['latitude'] = 10
        # Update the list of nearby recordings
        rc.update_request(self.req3)
        # verify that asset with largest 'weight' value is returned first
        self.assertEquals(self.asset7, rc.get_recording())
        self.assertEquals(self.asset4, rc.get_recording())
        self.assertEquals(None, rc.get_recording())

    def test_asset_blocking(self):
        """ Test that blocking an asset prevents it from being added
            to the playlist_proximity
        """
        # first create a user to perform the blocking
        # this should eventually be done 'globally' for this set of tests
        # but for now, this is the best way to ensure proper ordering
        url = reverse('user-list')
        data = {"device_id": "123456",
                "client_type": "phone",
                "client_system": "iOS"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check that a username was generated and token returned
        self.assertIsNotNone(response.data["username"])
        self.assertIsNotNone(response.data["token"])
        # set the token for later requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data["token"])

        # create stream prior to blocking asset and
        # verify all assets show up in playlist
        self.req1 = {"session_id": self.session4.id,
                     "project_id": self.project1.id,
                     "audio_stream_bitrate": '128',
                     "latitude": 0.1, "longitude": 0.1}
        req = self.req1
        stream = RoundStream(self.session4.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
        rc.update_request(req)
        self.assertEquals(self.asset3, rc.get_recording())
        self.assertEquals(self.asset2, rc.get_recording())
        self.assertEquals(self.asset1, rc.get_recording())
        self.assertEquals(None, rc.get_recording())

        # now block asset
        data = {"device_id": "123456",
                "session_id": self.session4.id,
                "vote_type": "block_asset"}
        url = '/api/2/assets/' + str(self.asset1.id) + '/votes/'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # generate new stream and verify that asset is blocked
        stream = RoundStream(self.session4.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
        rc.update_request(req)
        self.assertEquals(self.asset3, rc.get_recording())
        self.assertEquals(self.asset2, rc.get_recording())
        self.assertEquals(None, rc.get_recording())
