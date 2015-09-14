# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import logging

logger = logging.getLogger(__name__)


class SrcWavFile (gst.Bin):

    def __init__(self, uri, start, duration, fadein, fadeout, volume):
        gst.Bin.__init__(self)
        self.start = start
        self.duration = duration
        self.clip_volume = volume
        self.already_seeked = False
        self.fading = False

        self.src_wav_file = gst.element_factory_make("filesrc")
        self.src_wav_file.set_property("location", uri)
        self.decodebin = gst.element_factory_make("decodebin2")
        self.audioconvert = gst.element_factory_make("audioconvert")
        self.audioresample = gst.element_factory_make("audioresample")
        self.audiopanorama = gst.element_factory_make("audiopanorama")
        self.volume = gst.element_factory_make("volume")
        self.controller = gst.Controller(self.volume, "volume")
        self.controller.set_interpolation_mode(
            "volume", gst.INTERPOLATE_LINEAR)
        self.controller.set("volume", 0, 0.0)
        self.controller.set("volume", start, 0.0)
        self.controller.set("volume", start + fadein, volume)
        self.controller.set("volume", start + duration - fadeout, volume)
        self.controller.set("volume", start + duration, 0.0)
        self.add(self.src_wav_file, self.decodebin, self.audioconvert,
                 self.audioresample, self.audiopanorama, self.volume)
        gst.element_link_many(self.src_wav_file, self.decodebin)
        gst.element_link_many(self.audioconvert, self.audioresample,
                              self.audiopanorama, self.volume)

        def on_pad(comp, pad):
            convpad = self.audioconvert.get_compatible_pad(pad, pad.get_caps())
            pad.link(convpad)
        self.decodebin.connect("pad-added", on_pad)
        self.pad = self.volume.get_pad("src")
        self.ghostpad = gst.GhostPad("src", self.pad)
        self.add_pad(self.ghostpad)

    def seek_to_start(self):
        if not self.already_seeked:
            self.already_seeked = True
            self.decodebin.seek(
                1.0,
                gst.Format(gst.FORMAT_TIME),
                gst.SEEK_FLAG_ACCURATE,
                gst.SEEK_TYPE_SET,
                self.start,
                gst.SEEK_TYPE_SET,
                self.start + self.duration)

    def fade_out(self, nsecs):
        self.fading = True
        pos_int = self.decodebin.query_position(gst.FORMAT_TIME, None)[0]
        logger.debug("fade_out: got position: " + str(pos_int))
        self.controller.set_interpolation_mode(
            "volume", gst.INTERPOLATE_LINEAR)
        if (self.duration - pos_int) > nsecs:
            self.controller.set("volume", pos_int, self.clip_volume)
            self.controller.set("volume", pos_int + nsecs, 0)
        else:
            logger.debug("fade_out: letting it play out.")

    def pan_to(self, pos):
        self.audiopanorama.set_property("panorama", pos)

gobject.type_register(SrcWavFile)
