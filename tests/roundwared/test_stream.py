# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from model_mommy import mommy

from .common import RoundwaredTestCase
from roundware.rw.models import (MasterUI, Session, Tag, Asset, TagCategory,
                                 UIMapping, Project, LocalizedString)
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
                     "project_id": self.project1.id}
        self.asset1 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag1],
                                 audiolength=2000)
        self.asset2 = mommy.make(Asset, project=self.project1,
                                 language=self.english,
                                 tags=[self.tag1],
                                 audiolength=2000)

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
