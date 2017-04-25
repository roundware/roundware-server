# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import gobject
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q

from roundware.rw.models import calculate_volume, Speaker, Session

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

    def __init__(self, listener, project):
        gst.Bin.__init__(self)

        self.project = project

        self.sources = {}
        self.speakers = {}
        self.known_speakers = {}
        # find always on speakers
        always_on = Speaker.objects.filter(activeyn=True, project=self.project, minvolume__gt=0)
        if always_on.exists():
            logger.debug("Found speakers that are always on: {}".format(always_on))
            for speaker in always_on:
                self.speakers[speaker.id] = speaker
                self.inspect_speaker(speaker)

        logger.info("initializing GPSMixer")

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


    def inspect_speaker(self, speaker):

        if not self.known_speakers.get(speaker.id, False):
            if check_stream(speaker.uri):
                uri = speaker.uri
                logger.debug("taking normal uri: " + uri)
            elif check_stream(speaker.backupuri):
                uri = speaker.backupuri
                logger.warning("Stream " + speaker.uri + " is not a valid audio/mpeg stream. using backup.")
            else:
                logger.warning("Stream " + speaker.uri + " and backup are not valid audio/mpeg streams.")
                uri = None

            self.known_speakers[speaker.id] = {'speaker': speaker, 'uri': uri}

        return self.known_speakers.get(speaker.id)


    def remove_speaker_from_stream(self, speaker):

        logger.debug("fading audio to 0 before removing")
        self.sources[speaker.id].set_volume(0)

        src_to_remove = self.sources[speaker.id].get_pad('src')
        logger.debug("\t...removing {}".format(src_to_remove))
        logger.debug("\t...finding sinkpad")
        sinkpad = self.adder.get_request_pad("sink%d")

        logger.debug("\t...unlinking sinkpad")
        src_to_remove.unlink(sinkpad)

        logger.debug("\t...releasing sinkpad")
        self.adder.release_request_pad(sinkpad)

        logger.debug("\t...done!")


    def add_speaker_to_stream(self, speaker, volume):
        source = self.sources.get(speaker.id, None)
        if not source:
            validated_speaker = self.inspect_speaker(speaker)
            uri = validated_speaker['uri']
            if uri:
                tempsrc = src_mp3_stream.SrcMP3Stream(uri, volume)
                logger.debug("Allocated new source: {src} {uri}".format(src=tempsrc, uri=uri))
                logger.debug("Adding speaker: {s} ".format(s=speaker.id))
                self.sources[speaker.id] = tempsrc

                self.add(self.sources[speaker.id])
                logger.debug("\t...finding srcpad")
                srcpad = self.sources[speaker.id].get_pad('src')
                logger.debug("\t...finding addersinkpad")
                addersinkpad = self.adder.get_request_pad('sink%d')
                logger.debug("\t...linking addersinkpad")
                srcpad.link(addersinkpad)
                logger.debug("\t...setting speaker state to PLAYING")
                self.sources[speaker.id].set_state(gst.STATE_PLAYING)
                logger.debug("\t...done!")
            else:
                logger.debug("No valid uri for speaker")

    def set_speaker_volume(self, speaker, volume):
        source = self.sources.get(speaker.id, None)

        if not source:
            logger.debug("new speaker, adding to stream at {}".format(volume))
            self.add_speaker_to_stream(speaker, volume)
        else:
            logger.debug("already added, setting vol: " + str(volume))
        self.sources[speaker.id].set_volume(volume)

    def get_current_speakers(self):
        logger.info("filtering speakers")
        listener = Point(float(self.listener['longitude']), float(self.listener['latitude']))

        # filter speakers by geometry only for geo_listen projects;
        # otherwise include all active speakers for project/session
        sn = Session.objects.get(id=self.listener['session_id'][0])
        if sn.geo_listen_enabled:
            # get active speakers for this project, and select from those all speakers our listener is inside
            speakers = Speaker.objects.filter(activeyn=True, project=self.project).filter(
            Q(shape__dwithin=(listener, D(m=0))) | Q(minvolume__gt=0)
        )
        else:
            # add all active speakers regardless of geometry
            speakers = Speaker.objects.filter(activeyn=True, project=self.project)

        # make sure all the current speakers are registered in the self.speakers dict
        for s in speakers:
            self.speakers[s.id] = s
            self.inspect_speaker(s)

        return list(speakers)

    def move_listener(self, new_listener):

        self.listener = new_listener
        sn = Session.objects.get(id=self.listener['session_id'][0])

        # lookup speakers that should play in the db
        # and make sure they're in the self.speakers dict
        # we use this set to id speakers that should be off
        current_speakers = self.get_current_speakers()

        speakers_count = len(self.speakers.keys())
        logger.info("Processing {} speakers".format(speakers_count))

        for i, (_, speaker) in enumerate(self.speakers.items()):
            logger.info("Processing speaker {} of {}".format(i + 1, speakers_count))

            if speaker in current_speakers:
                logger.info("Speaker {} is within range. Calculating volume...".format(speaker.id))
                # only calculate volume if geo_listen project/session; otherwise set to maxvolume
                if sn.geo_listen_enabled:
                    vol = calculate_volume(speaker, self.listener)
                else:
                    logger.info("GLOBAL LISTEN: setting speaker volume to maxvolume = %s" % speaker.maxvolume)
                    vol = speaker.maxvolume
            else:
                logger.info("Speaker {} is out of range. Setting minvolume...".format(speaker.id))
                # set speakers that are not in range to minvolume
                vol = speaker.minvolume

            if vol == 0:
                logger.info("Speaker {} is off, removing from stream".format(speaker.id))
                self.remove_speaker_from_stream(speaker)
                logger.debug("Removed speaker: {}".format(speaker.id))
            else:
                logger.debug("Source # {} has a volume of {}".format(speaker.id, vol))
                self.set_speaker_volume(speaker, vol)

        logger.info("move listener complete")

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
