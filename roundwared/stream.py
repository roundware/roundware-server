#***********************************************************************************#

# ROUNDWARE
# a contributory, location-aware media platform

# Copyright (C) 2008-2014 Halsey Solutions, LLC
# with contributions from:
# Mike MacHenry, Ben McAllister, Jule Slootbeek and Halsey Burgund (halseyburgund.com)
# http://roundware.org | contact@roundware.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/lgpl.html>.

#***********************************************************************************#


import gobject
from roundware.rw.models import Tag

gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import logging
import time
from roundwared import settings, asset_sorters
from roundwared import composition
from roundwared import icecast2
from roundwared.server import icecast_mount_point
from roundwared import gpsmixer
from roundwared import recording_collection
from roundware.rw import models
from roundwared import db

logger = logging.getLogger(__name__)


class RoundStream:
    ######################################################################
    # PUBLIC
    ######################################################################

    def __init__(self, sessionid, audio_format, request):
        logger.debug("begin stream")
        self.sessionid = sessionid
        self.request = request
        self.bitrate = request["audio_stream_bitrate"]
        logger.debug("Roundstream init: bitrate: {0}".format(self.bitrate))
        logger.debug("Roundstream init: getting session id")
        session = models.Session.objects.select_related(
            'project').get(id=sessionid)
        logger.debug("Roundstream init: got session, getting project radius")
        self.radius = session.project.recording_radius
        self.ordering = session.project.ordering
        logger.debug(
            "Roundstream init: got session, got project radius: " + str(self.radius))
        if self.radius == None:
            self.radius = settings.config["recording_radius"]

        # TODO - Why is this stored as listener and as request?
        self.listener = request
        self.audio_format = audio_format
        self.last_listener_count = 1
        self.gps_mixer = None
        self.main_loop = gobject.MainLoop()
        self.icecast_admin = icecast2.Admin(
            settings.config["icecast_host"] + ":" +
            str(settings.config["icecast_port"]),
            settings.config["icecast_username"],
            settings.config["icecast_password"])
        self.heartbeat()
        # project = models.Session.objects.get(id=sessionid)  # not used
        self.recordingCollection = \
            recording_collection.RecordingCollection(
                self, request, self.radius, str(self.ordering))

    def start(self):
        logger.info("Serving stream" + str(self.sessionid))

        self.pipeline = gst.Pipeline()
        self.adder = gst.element_factory_make("adder")
        self.sink = RoundStreamSink(
            self.sessionid, self.audio_format, self.bitrate)
        self.pipeline.add(self.adder, self.sink)
        self.adder.link(self.sink)

        logger.info("Stream: start: Going to play: "
                    + ",".join(self.recordingCollection.get_filenames())
                    + " Total of "
                    + str(len(self.recordingCollection.get_filenames()))
                    + " files.")

        self.add_music_source()
        self.add_voice_compositions()
        self.add_message_watcher()

        self.pipeline.set_state(gst.STATE_PLAYING)
        gobject.timeout_add(
            settings.config["stereo_pan_interval"],
            self.stereo_pan)
        self.main_loop.run()

    def play_asset(self, request):
        asset_id = request['asset_id'][0]
        logger.debug("!!!!!!!!!! Stream Play asset: " + str(asset_id))
        for comp in self.compositions:
            comp.play_asset(asset_id)

    def skip_ahead(self):
        logger.debug("!!!!!!!!!!Skip ahead")
        for comp in self.compositions:
            comp.skip_ahead()

    # Sets the activity timestamp to right now.
    # The timestamp is used to detect
    # when the client last sent any message.
    def heartbeat(self):
        self.activity_timestamp = time.time()
        # logger.debug("update time="+str(self.activity_timestamp))

    def modify_stream(self, request):
        self.heartbeat()
        self.request = request
        self.listener = request
        self.refresh_recordings()
        logger.info("Stream modification: Going to play: "
                    + ",".join(self.recordingCollection.get_filenames())
                    + " Total of "
                    + str(len(self.recordingCollection.get_filenames()))
                    + " files.")
        self.move_listener(request)
        return True

    # Force the recording collection to get new recordings from the DB
    def refresh_recordings(self):
        self.recordingCollection.update_request(self.request)

        # filter recordings
        if "tags" in self.request:
            tag_ids = self.request["tags"]
            if not hasattr(tag_ids, "__iter__"):
                tag_ids = tag_ids.split(",")

            tags = Tag.objects.filter(pk__in=tag_ids)
            for tag in tags:
                if tag.filter:
                    logger.debug("Tag with filter found: %s: %s" %
                                 (tag, tag.filter))
                    self.recordingCollection.nearby_unplayed_recordings = getattr(asset_sorters, tag.filter)(
                        assets=self.recordingCollection.all_recordings, request=self.request)

        for comp in self.compositions:
            comp.move_listener(self.listener)

    def move_listener(self, listener):
        if listener['latitude'] != False and listener['longitude'] != False:
            logger.debug(
                "stream: move_listener: recvd lat and long, moving...")
            self.heartbeat()
            self.listener = listener
            logger.debug("move_listener("
                         + str(listener['latitude']) + ","
                         + str(listener['longitude']) + ")")
            if self.gps_mixer:
                self.gps_mixer.move_listener(listener)
            self.recordingCollection.move_listener(listener)
            # logger.info("Stream: move_listener: Going to play: " \
            #+ ",".join(self.recordingCollection.get_filenames()) \
            #+ " Total of " \
            #+ str(len(self.recordingCollection.get_filenames()))
            #+ " files.")
            for comp in self.compositions:
                comp.move_listener(listener)
        else:
            logger.debug(
                "stream: move_listener: no lat and long.  returning...")

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

    def add_music_source(self):
        p = models.Project.objects.get(id=self.request["project_id"])
        speakers = models.Speaker.objects.filter(
            project=p).filter(activeyn=True)
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

    def add_voice_compositions(self):
        p = models.Project.objects.get(id=self.request["project_id"])
        c = models.Audiotrack.objects.filter(project=p)
        logger.debug(
            "Stream: add_voice_compositions: got composition: " + str(c))
        self.compositions = []
        for t in c:
            self.compositions.append(composition.Composition(self,
                                                             self.pipeline,
                                                             self.adder,
                                                             t,
                                                             self.recordingCollection))

        # self.compositions = [composition.Composition(self,
            # self.pipeline,
            # self.adder,
            # c,
            # self.recordingCollection)]

        # TODO - ask if there is > 1 logical composition per proj. for now, assume 1 to 1.
        # self.compositions = \
            # map (lambda comp_settings:
            # composition.Composition(
            # self,
            # self.pipeline,
            # self.adder,
            # comp_settings,
            # self.recordingCollection),
            #[c])

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
            if message.src == self.pipeline \
                    and new == gst.STATE_PLAYING:
                logger.debug("Announcing " + str(self.sessionid)
                             + " is playing")
                gobject.timeout_add(
                    settings.config["ping_interval"],
                    self.ping)
                for comp in self.compositions:
                    comp.wait_and_play()

    def cleanup(self):
        db.log_event("cleanup_session", self.sessionid, None)
        logger.debug("Cleaning up" + str(self.sessionid))

        # db.cleanup_history_for_session(self.sessionid)
        if self.pipeline:
            if self.watch_id:
                self.pipeline.get_bus().remove_signal_watch()
                self.pipeline.get_bus().disconnect(self.watch_id)
                self.watch_id = None
            self.pipeline.set_state(gst.STATE_NULL)
        self.main_loop.quit()

    def stereo_pan(self):
        for comp in self.compositions:
            comp.stereo_pan()
        return True

    def ping(self):
        is_stream_active = \
            self.is_anyone_listening() \
            or self.is_activity_timestamp_recent()

        if is_stream_active:
            return True
        else:
            self.cleanup()
            return False

    def is_anyone_listening(self):
        listeners = self.icecast_admin.get_client_count(
            icecast_mount_point(
                self.sessionid, self.audio_format))
        # logger.debug("Number of listeners: " + str(listeners))
        if self.last_listener_count == 0 and listeners == 0:
            # logger.info("Detected noone listening.")
            return False
        else:
            self.last_listener_count = listeners
            return True

    def is_activity_timestamp_recent(self):
        # logger.debug("check now=" + str(time.time()) \
        #   + " time=" + str(self.activity_timestamp) \
        #   + " diff=" + str(time.time() - self.activity_timestamp))
        return time.time() - self.activity_timestamp < settings.config["heartbeat_timeout"]


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
        #self.taginjector = gst.element_factory_make("taginject")
        # self.taginjector.set_property("tags","title=\"asset_id=123\"")

        capsfilter = gst.element_factory_make("capsfilter")
        volume = gst.element_factory_make("volume")
        volume.set_property("volume", settings.config["master_volume"])
        shout2send = gst.element_factory_make("shout2send")
        shout2send.set_property(
            "username", settings.config["icecast_source_username"])
        shout2send.set_property(
            "password", settings.config["icecast_source_password"])
        #shout2send.set_property("username", "source")
        #shout2send.set_property("password", "roundice")
        shout2send.set_property("mount",
                                icecast_mount_point(sessionid, audio_format))
        #shout2send.set_property("streamname","initial name")
        #self.add(capsfilter, volume, self.taginjector, shout2send)
        self.add(capsfilter, volume, shout2send)
        capsfilter.link(volume)

        if audio_format.upper() == "MP3":
            capsfilter.set_property(
                "caps",
                gst.caps_from_string(
                    "audio/x-raw-int,rate=44100,channels=2,width=16,depth=16,signed=(boolean)true"))
            lame = gst.element_factory_make("lame")
            lame.set_property("bitrate", int(bitrate))
            logger.debug("roundstreamsink: bitrate: " + str(int(bitrate)))
            self.add(lame)
            #gst.element_link_many(volume, lame, self.taginjector, shout2send)
            gst.element_link_many(volume, lame, shout2send)
        elif audio_format.upper() == "OGG":
            capsfilter.set_property(
                "caps",
                gst.caps_from_string(
                    "audio/x-raw-float,rate=44100,channels=2,width=32"))
            vorbisenc = gst.element_factory_make("vorbisenc")
            oggmux = gst.element_factory_make("oggmux")
            self.add(vorbisenc, oggmux)
            #gst.element_link_many(volume, vorbisenc, oggmux, self.taginjector, shout2send)
            gst.element_link_many(volume, vorbisenc, oggmux, shout2send)
        else:
            raise "Invalid format"

        pad = capsfilter.get_pad("sink")
        ghostpad = gst.GhostPad("sink", pad)
        self.add_pad(ghostpad)
        #self.shout = shout2send
