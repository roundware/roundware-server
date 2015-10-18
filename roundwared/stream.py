# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import logging
import time
import urllib
from django.conf import settings
from roundware.rw import models
from roundware.lib.api import log_event
from roundwared.audiotrack import AudioTrack
from roundwared import icecast2
from roundwared import gpsmixer
from roundwared.recording_collection import RecordingCollection

logger = logging.getLogger(__name__)


class RoundStream:
    ######################################################################
    # PUBLIC
    ######################################################################

    def __init__(self, sessionid, audio_format, request):
        self.audiotracks = []
        self.sessionid = sessionid
        self.request = request
        self.bitrate = request["audio_stream_bitrate"]
        logger.debug("Roundstream init: bitrate: {0}".format(self.bitrate))
        session = models.Session.objects.select_related(
            'project').get(id=sessionid)
        self.project = session.project

        self.radius = self.project.recording_radius
        self.ordering = self.project.ordering
        # Keeps track of whether the stream has started playing audio.
        self.started = False

        logger.debug("Project radius: %d meters" % self.radius)
        if self.radius == None:
            self.radius = settings.RECORDING_RADIUS

        # TODO - Why is this stored as listener and as request?
        self.listener = request
        self.audio_format = audio_format
        self.last_listener_count = 1
        self.gps_mixer = None
        self.main_loop = gobject.MainLoop()
        self.icecast_admin = icecast2.Admin()
        self.heartbeat()
        self.recordingCollection = RecordingCollection(
                self, request, self.radius, str(self.ordering))

    def start(self):
        logger.info("Session %s - Starting stream", self.sessionid)

        self.pipeline = gst.Pipeline()
        self.adder = gst.element_factory_make("adder")
        self.sink = RoundStreamSink(
            self.sessionid, self.audio_format, self.bitrate)
        self.set_metadata({'stream_started': True})
        self.pipeline.add(self.adder, self.sink)
        self.adder.link(self.sink)

        self.add_speakers()
        self.add_audiotracks()
        self.add_message_watcher()

        self.pipeline.set_state(gst.STATE_PLAYING)
        gobject.timeout_add(settings.STEREO_PAN_INTERVAL, self.stereo_pan)
        self.main_loop.run()

    def play_asset(self, request):
        asset_id = request['asset_id'][0]
        logger.debug("Stream play asset: %s", asset_id)
        for track in self.audiotracks:
            track.play_asset(asset_id)

    def skip_ahead(self):
        logger.debug("Skip ahead")
        for track in self.audiotracks:
            track.skip_ahead()

    # Sets the activity timestamp to right now.
    # The timestamp is used to detect
    # when the client last sent any message.
    def heartbeat(self):
        self.activity_timestamp = time.time()

    # Sets the stream metadata using tag injection.
    def set_metadata(self, query):
        metadata = 'artist="Roundware",title="%s"' % urllib.urlencode(query)
        self.sink.taginjector.set_property("tags", metadata)

    def modify_stream(self, request):
        self.heartbeat()
        self.request = request
        self.listener = request
        # only refresh recordings if tags are present and not blank in request
        # NOT if only lat/lon are present; this prevents refresh_recordings from
        # happening on modify_streams that have only location changes
        if "tags" in self.request and self.request["tags"]:
            self.refresh_recordings()

        filenames = self.recordingCollection.get_filenames()
        logger.info("Stream modification: Going to play: " \
            + ",".join(filenames) \
            + " Total of " \
            + str(len(filenames))
            + " files.")
        self.move_listener(request)
        return True

    # Force the recording collection to get new recordings from the DB
    def refresh_recordings(self):
        self.recordingCollection.update_request(self.request)

    def move_listener(self, request):
        if request['latitude'] and request['longitude']:
            self.heartbeat()
            self.listener = request
            logger.debug("move_listener(%s,%s)", request['latitude'],
                         request['longitude'])
            if self.gps_mixer:
                self.gps_mixer.move_listener(request)
            self.recordingCollection.move_listener(request)
        else:
            logger.debug("no lat and long. Returning...")

    ######################################################################
    # PRIVATE
    ######################################################################
    def add_message_watcher(self):
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.watch_id = self.bus.connect("message", self.get_message)

    def add_source_to_adder(self, src_element):
        self.pipeline.add(src_element)
        srcpad = src_element.get_pad('src')
        addersinkpad = self.adder.get_request_pad('sink%d')
        srcpad.link(addersinkpad)

    def add_speakers(self):
        speakers = models.Speaker.objects.filter(
            project=self.project).filter(activeyn=True)
        # FIXME: We might need to unconditionally add blankaudio.
        # what happens if the only speaker is out of range? I think
        # it'll be fine but test this.
        if speakers.count() > 0:
            self.gps_mixer = gpsmixer.GPSMixer(
                {'latitude': self.request['latitude'],
                 'longitude': self.request['longitude']},
                speakers)
            self.add_source_to_adder(self.gps_mixer)
        else:
            self.add_source_to_adder(BlankAudioSrc())

    def add_audiotracks(self):
        settings = models.Audiotrack.objects.filter(project=self.project)
        logger.debug("Got AudioTrack Settings: %s" % settings)
        self.audiotracks = []
        for setting in settings:
            track = AudioTrack(self, self.pipeline, self.adder,
                                           setting, self.recordingCollection)
            self.audiotracks.append(track)

        # TODO - ask if there is > 1 logical audiotrack per proj. for now, assume 1 to 1.
        # self.audiotracks = \
            # map (lambda settings:
            # AudioTrack(
            # self,
            # self.pipeline,
            # self.adder,
            # settings,
            # self.recordingCollection),
            #[c])

    # Gst Pipeline Bus Signal watcher starts audiotracks when the stream is
    # available for ouput.
    def get_message(self, bus, message):
        # logger.debug(message.src.get_name() + str(message.type))
        if message.type == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            if err.message == "Could not read from resource.":
                logger.warning("Error reading file: "
                               + message.src.get_property("location"))
            else:
                logger.error("Error on " + str(self.sessionid)
                             + " from " + message.src.get_name() +
                             ": " + str(err) + " debug: " + debug)
                self.cleanup()
        elif message.type == gst.MESSAGE_STATE_CHANGED:
            prev, new, pending = message.parse_state_changed()
            # If the event message comes from the pipeline, the new state is
            # "playing" and we haven't already started the audiotracks, then
            # start everything.
            if message.src == self.pipeline and new == gst.STATE_PLAYING \
                    and not self.started:
                logger.debug("Stream for session %d has started." % self.sessionid)
                self.started = True
                gobject.timeout_add(settings.PING_INTERVAL, self.ping)
                self.recordingCollection.start()
                for track in self.audiotracks:
                    track.start_audio()

    def cleanup(self):
        log_event("cleanup_session", self.sessionid)
        logger.info("Session %d - Stream cleanup", self.sessionid)

        if self.pipeline:
            if self.watch_id:
                self.pipeline.get_bus().remove_signal_watch()
                self.pipeline.get_bus().disconnect(self.watch_id)
                self.watch_id = None
            self.pipeline.set_state(gst.STATE_NULL)
        self.main_loop.quit()

    def stereo_pan(self):
        for track in self.audiotracks:
            track.stereo_pan()
        return True

    def ping(self):
        is_stream_active = self.is_anyone_listening() \
            or self.is_activity_timestamp_recent()

        if is_stream_active:
            return True

        self.cleanup()
        return False

    def is_anyone_listening(self):
        mount_point = icecast2.mount_point(self.sessionid, self.audio_format)
        listeners = self.icecast_admin.get_client_count(mount_point)
        logger.debug("Number of listeners: %d " % listeners)
        if self.last_listener_count == 0 and listeners == 0:
            return False

        self.last_listener_count = listeners
        return True

    def is_activity_timestamp_recent(self):
        # logger.debug("check now=" + str(time.time()) \
        #   + " time=" + str(self.activity_timestamp) \
        #   + " diff=" + str(time.time() - self.activity_timestamp))
        return time.time() - self.activity_timestamp < settings.HEARTBEAT_TIMEOUT


# If there is no music this is needed to keep the stream not in
# and EOS state while there is dead air.
class BlankAudioSrc (gst.Bin):

    def __init__(self, wave=4):
        gst.Bin.__init__(self)
        audiotestsrc = gst.element_factory_make("audiotestsrc")
        audiotestsrc.set_property("wave", wave)  # 4 is silence
        audioconvert = gst.element_factory_make("audioconvert")
        self.add(audiotestsrc, audioconvert)
        audiotestsrc.link(audioconvert)
        pad = audioconvert.get_pad("src")
        ghost_pad = gst.GhostPad("src", pad)
        self.add_pad(ghost_pad)


class RoundStreamSink (gst.Bin):

    def __init__(self, sessionid, audio_format, bitrate):
        gst.Bin.__init__(self)

        capsfilter = gst.element_factory_make("capsfilter")
        volume = gst.element_factory_make("volume")
        volume.set_property("volume", settings.MASTER_VOLUME)
        # Create Metatag Injector
        self.taginjector = gst.element_factory_make("taginject")
        shout2send = gst.element_factory_make("shout2send")
        shout2send.set_property("username", settings.ICECAST_SOURCE_USERNAME)
        shout2send.set_property("password", settings.ICECAST_SOURCE_PASSWORD)
        shout2send.set_property("mount",
                                icecast2.mount_point(sessionid, audio_format))

        self.add(capsfilter, volume, self.taginjector, shout2send)
        capsfilter.link(volume)

        if audio_format.upper() == "MP3":
            capsfilter.set_property(
                "caps",
                gst.caps_from_string(
                    "audio/x-raw-int,rate=44100,channels=2,width=16,depth=16,signed=(boolean)true"))
            lame = gst.element_factory_make("lame")
            lame.set_property("bitrate", int(bitrate))
            logger.debug("roundstreamsink: bitrate: " + str(bitrate))
            self.add(lame)
            gst.element_link_many(volume, lame, self.taginjector, shout2send)
        elif audio_format.upper() == "OGG":
            capsfilter.set_property(
                "caps",
                gst.caps_from_string(
                    "audio/x-raw-float,rate=44100,channels=2,width=32"))
            vorbisenc = gst.element_factory_make("vorbisenc")
            oggmux = gst.element_factory_make("oggmux")
            self.add(vorbisenc, oggmux)
            gst.element_link_many(volume, vorbisenc, oggmux, self.taginjector, shout2send)
        else:
            raise "Invalid format"

        pad = capsfilter.get_pad("sink")
        ghostpad = gst.GhostPad("sink", pad)
        self.add_pad(ghostpad)
