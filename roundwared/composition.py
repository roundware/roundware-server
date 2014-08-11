# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# TODO: Figure out how to get the main pipeline to send EOS
#   when all compositions are finished (only happens
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
from roundwared import roundfilesrc
from roundwared import db
from django.conf import settings

STATE_PLAYING = 0
STATE_DEAD_AIR = 1
STATE_WAITING = 2
logger = logging.getLogger(__name__)


class Composition:
    ######################################################################
    # PUBLIC
    ######################################################################

    def __init__(self, parent, pipeline, adder, comp_settings, recordingColl):
        self.parent = parent
        # logger.debug("---------Composition init: self.parent class: " + self.parent.__class__.__name__)
        # logger.debug("---------Composition init: self.parent.sessionid: " + str(self.parent.sessionid))
        self.pipeline = pipeline
        self.adder = adder
        self.comp_settings = comp_settings
        self.recordingCollection = recordingColl
        self.current_pan_pos = 0
        self.target_pan_pos = 0
        self.state = STATE_WAITING
        self.roundfilesrc = None
        self.current_recording = None

    def wait_and_play(self):
        def callback():
            self.add_file()
            return False
        deadair = random.randint(
            self.comp_settings.mindeadair,
            self.comp_settings.maxdeadair) / gst.MSECOND
        gobject.timeout_add(deadair, callback)

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
            if self.roundfilesrc:
                self.roundfilesrc.pan_to(self.current_pan_pos)

    def move_listener(self, posn):
        if self.recordingCollection.has_recording():
            if self.state == STATE_WAITING:
                self.add_file()
# FIXME: This code is responsible for swapping the playing file if there is
#   a closer one to play and we've walked out of range of another.
#   Problem is it sounds bad without the ability to fade it out.
#   Uncomment this when fading works.
#           elif self.state == STATE_PLAYING:
#               if not self.recordingCollection.is_nearby(
#                       listener,
#                       self.currently_playing_recording):
# FIXME: This should fade out.
#                   self.clean_up()
#                   self.add_file()

    ######################################################################
    # PRIVATE
    ######################################################################

    def add_file(self):
        self.current_recording = self.recordingCollection.get_recording()
        if not self.current_recording:
            self.state = STATE_WAITING
            return

        duration = min(
            self.current_recording.audiolength,
            random.randint(
                # FIXME: I don't allow less than a second to
                # play currently. Mostly because playing zero
                # is an error. Revisit this.
                max(self.comp_settings.minduration,
                    gst.SECOND),
                max(self.comp_settings.maxduration,
                    gst.SECOND)))

        start = random.randint(
            0,
            self.current_recording.audiolength - duration)

        fadein = random.randint(
            self.comp_settings.minfadeintime,
            self.comp_settings.maxfadeintime)
        fadeout = random.randint(
            self.comp_settings.minfadeouttime,
            self.comp_settings.maxfadeouttime)

        # FIXME: Instead of doing this divide by two, instead,
        # decrease them by the same percentage. Remember it's
        # possible that fade_in != fade_out.
        if fadein + fadeout > duration:
            fadein = duration / 2
            fadeout = duration / 2

        volume = self.current_recording.volume * (
            self.comp_settings.minvolume +
            random.random() *
            (self.comp_settings.maxvolume -
                self.comp_settings.minvolume))

        logger.debug("current_recording.filename: %s, start: %s, duration: %s, fadein: %s, fadeout: %s, volume: %s",
                                self.current_recording.filename, start, duration, fadein, fadeout, volume)

        self.roundfilesrc = roundfilesrc.RoundFileSrc(
            "file://" + os.path.join(settings.MEDIA_ROOT,
                                     self.current_recording.filename),
            start, duration, fadein, fadeout, volume)
        self.pipeline.add(self.roundfilesrc)
        self.srcpad = self.roundfilesrc.get_pad('src')
        self.addersinkpad = self.adder.get_request_pad('sink%d')
        self.srcpad.link(self.addersinkpad)
        self.addersinkpad.add_event_probe(self.event_probe)
        (ret, cur, pen) = self.pipeline.get_state()
        self.roundfilesrc.set_state(cur)
        self.state = STATE_PLAYING
        # logger.debug("---------Composition add: self.parent.sink class: " + self.parent.sink.__class__.__name__)
        # self.parent.sink.taginjector.set_property("tags","title=\"asset_id=456\"")
        # logger.debug("trying...")
        # logger.debug("---------Composition add")
        # logger.debug("---------Composition add: self.parent class: " + self.parent.__class__.__name__)
        # logger.debug("---------Composition add: self.recording class: " + self.current_recording.__class__.__name__)
        # logger.debug("---------Composition add: self.parent.sessionid: " + str(self.parent.sessionid))
        # placeholder for refactor after we upgrade and fix taginject issue
        db.add_asset_to_session_history_and_update_metadata(
            self.current_recording.id, self.parent.sessionid, duration)
        # logger.debug("---------Composition add: self.parent.sink class: " + self.parent.sink.__class__.__name__)
        # logger.debug("---------Composition add: self.parent.sink.shout class: " + self.parent.sink.shout.__class__.__name__)
        #self.parent.sink.shout.set_property("streamname","asset" + str(self.current_recording.id))
        # logger.debug("made it!!!")

    def event_probe(self, pad, event):
        if event.type == gst.EVENT_EOS:
            gobject.idle_add(self.clean_up_wait_and_play)
        elif event.type == gst.EVENT_NEWSEGMENT:
            gobject.idle_add(self.roundfilesrc.seek_to_start)
        return True

    def clean_up_wait_and_play(self):
        self.clean_up()
        self.wait_and_play()

    def clean_up(self):
        if self.roundfilesrc:
            self.roundfilesrc.set_state(gst.STATE_NULL)
            self.pipeline.remove(self.roundfilesrc)
            self.adder.release_request_pad(self.addersinkpad)
            self.state = STATE_DEAD_AIR
            self.current_recording = None
            self.roundfilesrc = None
        return False

    def set_new_pan_target(self):
        pan_step_size = (self.comp_settings.maxpanpos -
                         self.comp_settings.minpanpos) / \
            settings.NUM_PAN_STEPS
        target_pan_step = random.randint(
            0,
            settings.NUM_PAN_STEPS)
        self.target_pan_pos = -1 + target_pan_step * pan_step_size

    def set_new_pan_duration(self):
        duration_in_gst_units = \
            random.randint(
                self.comp_settings.minpanduration,
                self.comp_settings.maxpanduration)
        duration_in_miliseconds = duration_in_gst_units / gst.MSECOND
        self.pan_steps_left = duration_in_miliseconds / \
            settings.STEREO_PAN_INTERVAL

    def skip_ahead(self):
        logger.debug("skip_ahead 1")
        fadeoutnsecs = random.randint(
            self.comp_settings.minfadeouttime,
            self.comp_settings.maxfadeouttime)
        if self.roundfilesrc != None and not self.roundfilesrc.fading:
            self.roundfilesrc.fade_out(fadeoutnsecs)
            logger.debug("skip_ahead 2")
            # 1st arg is in milliseconds
            # 1000000000
            #gobject.timeout_add(fadeoutnsecs/gst.MSECOND, self.clean_up_wait_and_play)
            logger.debug("skip_ahead 3")
            self.clean_up_wait_and_play()
        else:
            logger.debug("skip_ahead: no roundfilesrc")

    def play_asset(self, asset_id):
        logger.debug("Composition play asset: " + str(asset_id))
        self.recordingCollection.add_recording(asset_id)
        self.skip_ahead()
