from __future__ import unicode_literals
from model_mommy import mommy

from roundwared.recording_collection import RecordingCollection
from .common import RoundwaredTestCase
from roundware.rw.models import (Session, Asset, Project, Audiotrack)
from roundwared.stream import RoundStream
from roundwared.audiotrack import AudioTrack


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
                     "project_id": self.project1.id}
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

    def test_play_asset(self):
        req = self.req1
        req["audio_stream_bitrate"] = '128'
        stream = RoundStream(self.session1.id, 'ogg', req)
        #TODO: Create real mocks for this
        stream.pipeline = {}
        stream.adder = {}
        stream.add_audiotracks()
        stream.audiotracks[0].play_asset(self.asset1.id)
        self.assertEquals(stream.audiotracks[0].rc.playlist_proximity[0], self.asset1)
        self.assertFalse(stream.audiotracks[0].play_asset(10))