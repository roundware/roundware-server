from __future__ import unicode_literals
from model_mommy import mommy
from mock import patch

from .common import (RoundwaredTestCase, mock_distance_in_meters_near)
from roundware.rw.models import (Session, Asset,
                                 Project, MasterUI, UIMapping, Tag)
from roundwared.recording_collection import RecordingCollection
from roundwared.stream import RoundStream
from roundwared import gpsmixer
from roundwared import asset_sorters
from django.conf import settings
from time import sleep
settings.DEBUG = True


class TestRecordingCollection(RoundwaredTestCase):

    """ Exercise methods and instances of RecordingCollection
    """

    def setUp(self):
        super(type(self), TestRecordingCollection).setUp(self)

        self.project1 = mommy.make(Project, name='Project One',
                                   recording_radius=10,
                                   repeat_mode=Project.STOP)
        self.project2 = mommy.make(Project, name='Project One',
                                   recording_radius=20)
        self.session1 = mommy.make(Session, project=self.project1,
                                   language=self.english)
        self.session2 = mommy.make(Session, project=self.project2,
                                   language=self.english)
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
        self.masterui1 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=MasterUI.LISTEN,
                                    tag_category=self.tagcat1)
        self.masterui2 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=MasterUI.LISTEN,
                                    tag_category=self.tagcat1)
        self.uimapping1 = mommy.make(UIMapping, master_ui=self.masterui1,
                                     tag=self.tag1, default=True, active=True)
        self.uimapping2 = mommy.make(UIMapping, master_ui=self.masterui1,
                                     tag=self.tag2, default=True, active=True)

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
        # Wait for the BANNED_TIMEOUT_LIMIT to pass
        sleep(3)
        # Move back
        req['latitude'] = 0.1
        rc.move_listener(req)
        # Check the assets are available again.
        self.assertEquals(self.asset3, rc.get_recording())
        self.assertEquals(self.asset2, rc.get_recording())
        self.assertEquals(self.asset1, rc.get_recording())

    def test_get_recording_until_none_repeatmode_continuous(self):
        """ test that we get the next playlist_proximity nearby recording, until there
        are none left.  project in continuous repeatmode should then the
        first played recording.
        """
        self.project1.repeat_mode = Project.CONTINOUS
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
            self.assertEquals(self.asset3, rc.get_recording())

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
            rc.add_recording(self.asset2.id)
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
