# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from model_mommy import mommy

from .common import RoundwaredTestCase
from roundware.rw.models import (UIGroup, Session, Tag, Asset, TagCategory,
                                 UIItem, Project, LocalizedString, Audiotrack)
from roundwared.stream import RoundStream

class TestRoundStream(RoundwaredTestCase):

    """ Exercise methods and instances of RoundStream
    """

    def setUp(self):
        super(type(self), TestRoundStream).setUp(self)

        self.project1 = mommy.make(Project, name='Project One',
                                   ordering='random', recording_radius=16)
        self.session1 = mommy.make(Session, project=self.project1,
                                   language=self.english)
        self.req1 = {"session_id": self.session1.id,
                     "project_id": self.project1.id,
                     "latitude":1.0,
                     "longitude":1.0}
        self.asset1 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag1],
                                 audiolength=2000)
        self.asset2 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag1],
                                 audiolength=2000)
        self.audiotrack = mommy.make(Audiotrack, project=self.project1,
                                     minvolume=1.0,
                                     maxvolume=1.0,
                                     minduration=10000000000.0,
                                     maxduration=30000000000.0,
                                     mindeadair=1000000000.0,
                                     maxdeadair=3000000000.0,
                                     minfadeintime=100000000.0,
                                     maxfadeintime=500000000.0,
                                     minfadeouttime=100000000.0,
                                     maxfadeouttime=2000000000.0,
                                     minpanpos=0.0,
                                     maxpanpos=0.0,
                                     minpanduration=5000000000.0,
                                     maxpanduration=10000000000.0)

    def test_new_stream_has_recording_collection(self):
        """ Instantiate a new RoundStream.  Should have a RecordingCollection
        """
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        self.assertEquals(stream.recordingCollection.__class__.__name__,
                          'RecordingCollection')

    def test_new_stream_has_correct_radius_from_project(self):
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        self.assertEquals(16, stream.radius)

    def test_modify_stream(self):
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        req["latitude"] = 1
        req["longitude"] = 1
        stream.modify_stream(req)

    def test_new_stream_ordering_from_project(self):
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        self.assertEquals('random', stream.ordering)

    def test_main_loop(self):
        """ make sure we get a gObject MainLoop """
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        self.assertEquals(stream.main_loop.__class__.__name__, 'MainLoop')

    def test_icecast_admin_instantiated(self):
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        admin = stream.icecast_admin
        self.assertEquals(admin.__class__.__name__, 'Admin')

    def test_stream_get_state(self):
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        self.assertEqual(stream.get_state(), 0)
        stream.resume()
        self.assertEqual(stream.get_state(), 1)

    def test_pause_stream(self):
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        stream.pause()
        self.assertTrue(stream.is_paused())

    def test_resume_stream(self):
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        stream.resume()
        self.assertFalse(stream.is_paused())

    def test_add_audiotrack(self):
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        stream.pipeline = {}
        stream.adder = {}
        self.assertEqual(len(stream.audiotracks), 0)
        stream.add_audiotracks()
        self.assertEqual(len(stream.audiotracks), 1)