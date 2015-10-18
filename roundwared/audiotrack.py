# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# TODO: Figure out how to get the main pipeline to send EOS
#   when all audiotracks are finished (only happens
#   when repeat is off)
# TODO: Reimplement panning using a gst.Controller
# TODO: Remove stero_pan from public interface

from __future__ import unicode_literals
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import random
import logging
import os
from roundwared import src_wav_file
from roundwared import db
from django.conf import settings

STATE_PLAYING = 0
STATE_DEAD_AIR = 1
STATE_WAITING = 2
logger = logging.getLogger(__name__)


class AudioTrack:
    ######################################################################
    # PUBLIC
    ######################################################################

    def __init__(self, stream, pipeline, adder, settings, recording_collection):
        self.stream = stream
        self.pipeline = pipeline
        self.adder = adder
        self.settings = settings
        self.rc = recording_collection
        self.current_pan_pos = 0
        self.target_pan_pos = 0
        self.state = STATE_DEAD_AIR
        self.src_wav_file = None
        self.current_recording = None
        # Incremented only after start_audio() is called.
        self.track_timer = 0

    def start_audio(self):
        """
        Called once to start the audio manager timer
        """
        def asset_start_timer():
            """
            The asset timer runs once to start new assets after a certain
            amount of dead air.

            gobject timeout callbacks are repeated until they return False.
            """
            self.add_file()
            return False

        def track_timer():
            """
            The audio manager.

            Timeout called every second to maintain the audio asset stream.
            """
            # logger.debug("TickTock: %s" % self.track_timer)
            self.track_timer += 1

            # Do nothing if audio is playing already.
            if self.state == STATE_PLAYING:
                return True
            # No audio playing and asset_timer_callback is not scheduled, this
            # is set by self.clean_up() when an asset ends.
            elif self.state == STATE_DEAD_AIR:
                self.state = STATE_WAITING
                # Generate a random amount of dead air.
                deadair = random.randint(
                    self.settings.mindeadair,
                    self.settings.maxdeadair) / gst.MSECOND
                # Attempt to start an asset in the future.
                gobject.timeout_add(deadair, asset_start_timer)
            return True

        # http://www.pygtk.org/pygtk2reference/gobject-functions.html#function-gobject--timeout-add
        # Call audio_timer_callback() every second.
        gobject.timeout_add(1000, track_timer)

    def stereo_pan(self):
        if self.current_pan_pos == self.target_pan_pos \
                or self.pan_steps_left == 0:
            self.set_new_pan_target()
            self.set_new_pan_duration()
        else:
            pan_distance = \
                self.target_pan_pos - self.current_pan_pos
            amount_to_pan_now = pan_distance / self.pan_steps_left
            self.current_pan_pos += amount_to_pan_now
            self.pan_steps_left -= 1
            if self.src_wav_file:
                self.src_wav_file.pan_to(self.current_pan_pos)

    ######################################################################
    # PRIVATE
    ######################################################################

    def add_file(self):
        self.current_recording = self.rc.get_recording()
        if not self.current_recording:
            self.state = STATE_DEAD_AIR
            self.set_track_metadata()
            return

        duration = min(
            self.current_recording.audiolength,
            random.randint(
                # FIXME: I don't allow less than a second to
                # play currently. Mostly because playing zero
                # is an error. Revisit this.
                max(self.settings.minduration,
                    gst.SECOND),
                max(self.settings.maxduration,
                    gst.SECOND)))

        start = random.randint(
            0,
            self.current_recording.audiolength - duration)

        fadein = random.randint(
            self.settings.minfadeintime,
            self.settings.maxfadeintime)
        fadeout = random.randint(
            self.settings.minfadeouttime,
            self.settings.maxfadeouttime)

        # FIXME: Instead of doing this divide by two, instead,
        # decrease them by the same percentage. Remember it's
        # possible that fade_in != fade_out.
        if fadein + fadeout > duration:
            fadein = duration / 2
            fadeout = duration / 2

        volume = self.current_recording.volume * (
            self.settings.minvolume +
            random.random() *
            (self.settings.maxvolume -
                self.settings.minvolume))

        # logger.debug("current_recording.filename: %s, start: %s, duration: %s, fadein: %s, fadeout: %s, volume: %s",
        #                        self.current_recording.filename, start, duration, fadein, fadeout, volume)
        logger.info("Session %s - Playing asset %s filename: %s, duration: %.2f secs" %
                    (self.stream.sessionid, self.current_recording.id,
                     self.current_recording.filename, duration / 1000000000.0))

        self.src_wav_file = src_wav_file.SrcWavFile(
            os.path.join(settings.MEDIA_ROOT,
                         self.current_recording.filename),
            start, duration, fadein, fadeout, volume)
        self.pipeline.add(self.src_wav_file)
        self.srcpad = self.src_wav_file.get_pad('src')
        self.addersinkpad = self.adder.get_request_pad('sink%d')
        self.srcpad.link(self.addersinkpad)
        # Add event watcher/callback
        self.addersinkpad.add_event_probe(self.event_probe)
        (ret, cur, pen) = self.pipeline.get_state()
        self.src_wav_file.set_state(cur)
        self.state = STATE_PLAYING

        # Generate metadata for the current asset.
        tags = [str(tag.id) for tag in self.current_recording.tags.all()]
        self.set_track_metadata({'asset': self.current_recording.id,
                   'tags': ','.join(tags)})

        db.add_asset_to_session_history(
            self.current_recording.id, self.stream.sessionid, duration)

    def event_probe(self, pad, event):
        # End of current audio asset, start a new asset.
        if event.type == gst.EVENT_EOS:
            self.set_track_metadata({'asset': self.current_recording.id,
                        'complete': True, })
            gobject.idle_add(self.clean_up)
        # New asset added, seek to it's starting timestamp.
        elif event.type == gst.EVENT_NEWSEGMENT:
            gobject.idle_add(self.src_wav_file.seek_to_start)
        return True

    def clean_up(self):
        if self.src_wav_file:
            self.src_wav_file.set_state(gst.STATE_NULL)
            self.pipeline.remove(self.src_wav_file)
            self.adder.release_request_pad(self.addersinkpad)
            self.state = STATE_DEAD_AIR
            self.current_recording = None
            self.src_wav_file = None
        return False

    def set_new_pan_target(self):
        pan_step_size = (self.settings.maxpanpos -
                         self.settings.minpanpos) / \
            settings.NUM_PAN_STEPS
        target_pan_step = random.randint(0, settings.NUM_PAN_STEPS)
        self.target_pan_pos = -1 + target_pan_step * pan_step_size

    def set_new_pan_duration(self):
        duration_in_gst_units = \
            random.randint(
                self.settings.minpanduration,
                self.settings.maxpanduration)
        duration_in_miliseconds = duration_in_gst_units / gst.MSECOND
        self.pan_steps_left = duration_in_miliseconds / \
            settings.STEREO_PAN_INTERVAL

    def skip_ahead(self):
        fadeoutnsecs = random.randint(
            self.settings.minfadeouttime,
            self.settings.maxfadeouttime)
        if self.src_wav_file != None and not self.src_wav_file.fading:
            self.src_wav_file.fade_out(fadeoutnsecs)
            # 1st arg is in milliseconds
            # 1000000000
            #gobject.timeout_add(fadeoutnsecs/gst.MSECOND, self.clean_up)
            self.clean_up()
        else:
            logger.debug("skip_ahead: no src_wav_file")

    def play_asset(self, asset_id):
        logger.debug("AudioTrack play asset: " + str(asset_id))
        self.rc.add_recording(asset_id)
        self.skip_ahead()

    def set_track_metadata(self, metadata={}):
        """
        Sets Audiotrack specific metadata.
        """
        data = {'audiotrack': self.settings.id,
                'remaining': self.rc.count(),
                }
        data.update(metadata)
        self.stream.set_metadata(data)
