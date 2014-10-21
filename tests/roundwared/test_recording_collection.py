from __future__ import unicode_literals
from model_mommy import mommy
from mock import patch

from .common import (RoundwaredTestCase, mock_distance_in_meters_far,
                     mock_distance_in_meters_near)
from roundware.rw.models import (Session, Asset, Project, MasterUI, UIMapping)
from roundwared.recording_collection import RecordingCollection
from roundwared.stream import RoundStream
from roundwared import gpsmixer
from roundwared import asset_sorters


class TestRecordingCollection(RoundwaredTestCase):

    """ Exercise methods and instances of RecordingCollection
    """

    def setUp(self):
        super(type(self), TestRecordingCollection).setUp(self)

        self.project1 = mommy.make(Project, name='Project One',
                                   recording_radius=10,
                                   repeat_mode__mode="stop")
        self.project2 = mommy.make(Project, name='Project One',
                                   recording_radius=20)
        self.session1 = mommy.make(Session, project=self.project1,
                                   language=self.english)
        self.session2 = mommy.make(Session, project=self.project2,
                                   language=self.english)
        self.req1 = {"session_id": self.session1.id,
                     "project_id": self.project1.id,
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
        self.masterui1 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=self.ui_mode_listen,
                                    tag_category=self.tagcat1)
        self.masterui2 = mommy.make(MasterUI, project=self.project1,
                                    ui_mode=self.ui_mode_listen,
                                    tag_category=self.tagcat1)
        self.uimapping1 = mommy.make(UIMapping, master_ui=self.masterui1,
                                     tag=self.tag1, default=True, active=True)


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
        self.assertEquals([self.asset1, self.asset2], rc.all)

    def test_correct_far_recordings(self):
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)

        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius)
            # Update the list of nearby recordings
            rc.update_request(req)

            self.assertEquals([], rc.far)  # everything close by

        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_far):
            rc2 = RecordingCollection(stream, req, stream.radius)  # all far
            self.assertEquals([self.asset1, self.asset2], rc2.far)

    def test_update_request_all_recordings_changes(self):
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        rc = RecordingCollection(stream, req, stream.radius)
        req['session_id'] = self.session2.id
        rc.update_request(req)
        self.assertEquals([], rc.all)

    def test_update_request_far_recordings_changes(self):
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_far):
            rc.update_request(req)
            self.assertEquals([self.asset1, self.asset2], rc.far)

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
                rc.update_nearby_recordings(req)
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
        vote1, vote2, vote3 # Use all three votes to stop unuse warnings
        self.assertEquals([self.asset1, self.asset2],
                          asset_sorters.order_assets_by_like([self.asset1, self.asset2]))

    def test_order_assets_by_weight(self):
        """
        Order of assets returned should be determined by asset weight
        List is reverse order because assets are popped off the stack.
        """
        self.assertEquals([self.asset1, self.asset2],
                          asset_sorters.order_assets_by_weight([self.asset1,
                                                     self.asset2]))

    def test_get_recording_until_none_repeatmode_stop(self):
        """ test that we get the next unplayed nearby recording, until there
        are none left.  project in stop repeatmode should then not 
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

            next_rec = rc.get_recording()
            self.assertEquals(self.asset2, next_rec)
            next_rec = rc.get_recording()
            self.assertEquals(self.asset1, next_rec)
            next_rec = rc.get_recording()
            self.assertEquals(None, next_rec)

    def test_get_recording_until_none_repeatmode_continuous(self):
        """ test that we get the next unplayed nearby recording, until there
        are none left.  project in continuous repeatmode should then the
        first played recording 
        """
        self.project1.repeat_mode.mode = "continuous"
        self.project1.repeat_mode.save()
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
            # Update the list of nearby recordings
            rc.update_request(req)

            next_rec = rc.get_recording()
            self.assertEquals(self.asset2, next_rec)
            next_rec = rc.get_recording()
            self.assertEquals(self.asset1, next_rec)
            next_rec = rc.get_recording()
            self.assertEquals(self.asset2, next_rec)

    def test_get_recording_passing_session_not_matching_project(self):
        pass

    def test_add_recording(self):
        """ add a specific asset id and it should show up in
        nearby_unplayed
        """
        req = self.req1
        stream = RoundStream(self.session1.id, 'ogg', req)
        with patch.object(gpsmixer, 'distance_in_meters',
                          mock_distance_in_meters_near):
            rc = RecordingCollection(stream, req, stream.radius, 'by_weight')
            # Update the list of nearby recordings
            rc.update_request(req)
            self.assertEquals([self.asset1, self.asset2],
                              rc.nearby_unplayed)
            rc.add_recording(self.asset2.id)
            self.assertEquals([self.asset1, self.asset2, self.asset2],
                              rc.nearby_unplayed)
