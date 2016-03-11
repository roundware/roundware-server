# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals

import gobject
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from roundware.rw.models import calculate_volume, Speaker

gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import logging
import math
import httplib
import urlparse
import src_mp3_stream
logger = logging.getLogger(__name__)


class GPSMixer (gst.Bin):

    def __init__(self, listener, speakers):

        logger.debug("initializing GPSMixer")
        gst.Bin.__init__(self)
        self.sources = {}
        self.speakers = {}
        self.adder = gst.element_factory_make("adder")
        self.add(self.adder)
        pad = self.adder.get_pad("src")
        ghostpad = gst.GhostPad("src", pad)
        self.add_pad(ghostpad)
        addersinkpad = self.adder.get_request_pad('sink%d')
        logger.debug("Adding blank audio")
        blanksrc = BlankAudioSrc2()
        self.add(blanksrc)
        srcpad = blanksrc.get_pad('src')
        srcpad.link(addersinkpad)
        logger.info("iterating through " + str(len(speakers)) + " speakers.")
        for speaker in speakers:
            vol = calculate_volume(speaker, listener)
            uri = None
            if check_stream(speaker.uri):
                uri = speaker.uri
                logger.debug("taking normal uri: " + uri)
            elif check_stream(speaker.backupuri):
                uri = speaker.backupuri
                logger.warning("Stream " + speaker.uri
                               + " is not a valid audio/mpeg stream."
                               + " using backup.")
            else:
                logger.warning("Stream " + speaker.uri
                               + " and backup "
                               #+ speaker['backupuri']
                               + " are not valid audio/mpeg streams."
                               + " Not adding anything.")
                continue

            logger.debug("vol is " + str(vol) + " for uri " + uri)
            if vol > 0:
                logger.debug("adding to bin")
                src = src_mp3_stream.SrcMP3Stream(uri, vol)
                self.add(src)
                srcpad = src.get_pad('src')
                addersinkpad = self.adder.get_request_pad('sink%d')
                srcpad.link(addersinkpad)
                self.sources[speaker.id] = src
            else:
                logger.debug("appending")
                self.sources[speaker.id] = None
            self.speakers[speaker.id] = speaker

        self.projects = set([speaker.project for _, speaker in self.speakers.items()])
        self.move_listener(listener)

    def remove_speaker_from_stream(self, speaker):
        source = self.sources.get(speaker.id, None)

        if not source:
            return
        logger.debug("fading audio to 0 before removing")
        source.set_volume(0)
        src_to_remove = source.get_pad('src')
        sinkpad = self.adder.get_request_pad("sink%d")
        src_to_remove.unlink(sinkpad)
        self.adder.release_request_pad(sinkpad)
        self.remove(src_to_remove)

        del self.sources[speaker.id]
        del self.speakers[speaker.id]

    def add_speaker_to_stream(self, speaker, volume):
        logger.debug("Allocating new source")
        tempsrc = src_mp3_stream.SrcMP3Stream(speaker.uri, volume)
        source = tempsrc
        self.add(source)
        srcpad = source.get_pad('src')
        addersinkpad = self.adder.get_request_pad('sink%d')
        srcpad.link(addersinkpad)

    def set_speaker_volume(self, speaker, volume):
        source = self.sources.get(speaker.id, None)

        if not source:
            self.add_speaker_to_stream(speaker, volume)
        else:
            logger.debug("already added, setting vol: " + str(volume))
            source.set_volume(volume)

    @property
    def current_speakers(self):
        logger.info("filtering speakers")
        listener = Point(float(self.listener['longitude']), float(self.listener['latitude']))
        speakers = Speaker.objects.filter(shape__dwithin=(listener, D(m=0)), activeyn=True)
        if self.projects:
            speakers = speakers.filter(project__in=self.projects)
        logger.info(speakers)
        return list(speakers)

    def move_listener(self, new_listener):

        self.listener = new_listener

        current_speakers = self.current_speakers

        for speaker in current_speakers:
            self.speakers[speaker.id] = speaker

        for _, speaker in self.speakers.items():

            if speaker in current_speakers:
                vol = calculate_volume(speaker, self.listener)
            else:
                # set speakers that are not in range to minvolume
                vol = speaker.minvolume

            logger.debug("Source # %s has a volume of %s" % (speaker.id, vol))

            if vol == 0:
                logger.debug("Speaker is off, removing from stream")
                self.remove_speaker_from_stream(speaker)
                logger.debug("Removed speaker: %s" % speaker.id)
            else:
                self.set_speaker_volume(speaker, vol)


def lg(x):
    return math.log(x) / math.log(2)


def distance_in_meters(lat1, lon1, lat2, lon2):
    return distance_in_km(lat1, lon1, lat2, lon2) * 1000


def distance_in_km(lat1, lon1, lat2, lon2):
    # logger.debug(str.format("distance_in_km: lat1: {0}, lon1: {1}, lat2: {2}, lon2: {3}", lat1, lon1, lat2, lon2))
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d


def check_stream(url):
    try:
        o = urlparse.urlparse(url)
        h = httplib.HTTPConnection(o.hostname, o.port, timeout=10)
        h.request('GET', o.path)
        r = h.getresponse()
        content_type = r.getheader('content-type')
        h.close()
        return content_type == 'audio/mpeg'
    except:
        return False


class BlankAudioSrc2 (gst.Bin):

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
