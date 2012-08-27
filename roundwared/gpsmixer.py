import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import logging
import math
import httplib
import urlparse
from roundwared import gnomevfsmp3src
from roundwared import settings

class GPSMixer (gst.Bin):
	def __init__ (self, listener, speakers):
		gst.Bin.__init__(self)
		self.sources = []
		self.speakers = []
		self.adder = gst.element_factory_make("adder")
		self.add(self.adder)
		pad = self.adder.get_pad("src")
		ghostpad = gst.GhostPad("src", pad)
		self.add_pad(ghostpad)
		addersinkpad = self.adder.get_request_pad('sink%d')
		logging.debug("adding blank src.")
		blanksrc = BlankAudioSrc2()
		self.add(blanksrc)
		srcpad = blanksrc.get_pad('src')
		srcpad.link(addersinkpad)
		logging.debug("adding blank src - ADDED")
		logging.debug("iterating through " + str(len(speakers)) + " speakers.")
		for speaker in speakers:
			vol = calculate_volume(speaker, listener)
			uri = None
			if check_stream(speaker.uri):
				uri = speaker.uri
				logging.debug("taking normal uri: " + uri)
			elif check_stream(speaker.backupuri):
				uri = speaker.backupuri
				logging.warning("Stream " + speaker.uri \
					+ " is not a valid audio/mpeg stream." \
					+ " using backup.")
			else:
				logging.warning("Stream " + speaker.uri \
					+ " and backup " \
					#+ speaker['backupuri'] \
					+ " are not valid audio/mpeg streams." \
					+ " Not adding anything.")
				continue
			
			logging.debug("vol is " + str(vol) + " for uri " + uri)
			if vol > 0:
				logging.debug("adding to bin")
				src = gnomevfsmp3src.GnomeVFSMP3Src(uri, vol)
				self.add(src)
				srcpad = src.get_pad('src')
				addersinkpad = self.adder.get_request_pad('sink%d')
				srcpad.link(addersinkpad)
				self.sources.append(src)
			else:
				logging.debug("appending")
				self.sources.append(None)			
			self.speakers.append(speaker)
		self.move_listener(listener)

	def move_listener (self, new_listener):
		self.listener = new_listener
		for i in range(len(self.speakers)):
			vol = calculate_volume(self.speakers[i], self.listener)
			logging.debug("gpsmixer: move_listener: source # " + str(i) + " has a volume of " + str(vol))
			if vol > 0:
				if self.sources[i] == None:
					logging.debug("gpsmixer: move_listener: allocating new source")
					tempsrc = gnomevfsmp3src.GnomeVFSMP3Src(self.speakers[i].uri, vol)
					logging.debug("gpsmixer: move_listener: replacing old slot in source array")
					self.sources[i] = tempsrc
					logging.debug("gpsmixer: move_listener: adding speaker: "  + str(self.speakers[i].id))
					self.add(self.sources[i])
					#self.set_state(gst.STATE_PLAYING)

					srcpad = self.sources[i].get_pad('src')
					addersinkpad = self.adder.get_request_pad('sink%d')
					srcpad.link(addersinkpad)
					self.sources[i].set_state(gst.STATE_PLAYING)
					logging.debug("gpsmixer: move_listener: adding speaker SUCCESS")
					#self.set_state(gst.STATE_PLAYING)
				else:
					logging.debug("already added, setting vol: " + str(vol))
					self.sources[i].set_volume(vol)

			else:
				logging.debug("gpsmixer: move_listener: checking if speaker is already added, prior to removal")
				if self.sources[i] != None:
					self.sources[i].set_volume(vol)
					logging.debug("gpsmixer: move_listener: removing speaker: "  + str(self.speakers[i].id))
					src_to_remove = self.sources[i].get_pad('src')
					logging.debug("gpsmixer: move_listener: removing speaker1")
					#src_to_remove.set_blocked(True)
					logging.debug("gpsmixer: move_listener: removing speaker2")
					#we crash whenever we set state to NULL, either here or after unlinking
					#self.sources[i].set_state(gst.STATE_NULL)
					logging.debug("gpsmixer: move_listener: removing speaker3")
					sinkpad = self.adder.get_request_pad("sink%d")
					logging.debug("gpsmixer: move_listener: removing speaker4")
					src_to_remove.unlink(sinkpad)
					logging.debug("gpsmixer: move_listener: removing speaker5")
					self.adder.release_request_pad(sinkpad)
					logging.debug("gpsmixer: move_listener: removing speaker6")
					#self.remove(self.sources[i])
					logging.debug("gpsmixer: move_listener: removing speaker - SUCCESS")
					#self.sources[i] = None
					#self.set_state(gst.STATE_PLAYING)
				
# FIXME: Attenuation is linear.
def calculate_volume (speaker, listener):
	distance = distance_in_meters(
		listener['latitude'],
		listener['longitude'],
		speaker.latitude,
		speaker.longitude)
	vol = 0
	if (distance <= speaker.mindistance):
		vol = speaker.maxvolume
	elif (distance >= speaker.maxdistance):
		vol = speaker.minvolume
	else:
		vol_frac = math.pow(
			2,
			lg(distance/speaker.mindistance))
		vol = speaker.maxvolume / vol_frac
	#logging.debug(
		#"Speaker: id=" + str(speaker.id) + \
		#" uri=" + speaker.uri + \
		#" distance=" + str(distance) + \
		#" volume=" + str(vol))
	return vol

def lg (x):
	return math.log(x) / math.log(2)

def distance_in_meters (lat1, lon1, lat2, lon2):
	return distance_in_km(lat1, lon1, lat2, lon2) * 1000

def distance_in_km (lat1, lon1, lat2, lon2):
	#logging.debug(str.format("distance_in_km: lat1: {0}, lon1: {1}, lat2: {2}, lon2: {3}", lat1, lon1, lat2, lon2))
	R = 6371
	dLat = math.radians(lat2-lat1)
	dLon = math.radians(lon2-lon1)
	a = math.sin(dLat/2) * math.sin(dLat/2) + \
		math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
		math.sin(dLon/2) * math.sin(dLon/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
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
	def __init__ (self, wave = 4):
		gst.Bin.__init__(self)
		audiotestsrc = gst.element_factory_make("audiotestsrc")
		audiotestsrc.set_property("wave", wave) #4 is silence
		audioconvert = gst.element_factory_make("audioconvert")
		self.add(audiotestsrc, audioconvert)
		audiotestsrc.link(audioconvert)
		pad = audioconvert.get_pad("src")
		ghost_pad = gst.GhostPad("src", pad)
		self.add_pad(ghost_pad)