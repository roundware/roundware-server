import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst

VOLUME_CHANGE_INTERVAL = 100 #milliseconds
VOLUME_CHANGE_STEP = 0.01 #gsttreamer volume units

class GnomeVFSMP3Src (gst.Bin):

	def __init__ (self, uri, vol = 1.0):
		gst.Bin.__init__(self)
		self.is_adjusting = False
		gnomevfssrc = gst.element_factory_make("gnomevfssrc")
		gnomevfssrc.set_property("location", uri)
		mad = gst.element_factory_make("mad")
		audioconvert = gst.element_factory_make("audioconvert")
		audioresample = gst.element_factory_make("audioresample")
		self.current_vol = vol
		self.target_vol = vol
		self.volume = gst.element_factory_make("volume")
		self.volume.set_property("volume", self.current_vol)
		self.add(gnomevfssrc, mad, audioconvert,
			audioresample, self.volume)
		gst.element_link_many(gnomevfssrc, mad,
			audioconvert, audioresample, self.volume)
		pad = self.volume.get_pad("src")
		ghostpad = gst.GhostPad("src", pad)
		self.add_pad(ghostpad)

	def set_volume (self, vol):
		self.target_vol = vol
		if self.target_vol != self.current_vol \
			and not self.is_adjusting:

			self.is_adjusting = True
			gobject.timeout_add(
				VOLUME_CHANGE_INTERVAL,
				self.adjust_volume)

	def adjust_volume (self):
		new_vol = calculate_new_volume(
			self.current_vol,
			self.target_vol)
		self.current_vol = new_vol
		self.volume.set_property("volume", self.current_vol)
		self.is_adjusting = self.current_vol != self.target_vol
		return self.is_adjusting

def calculate_new_volume (current, target):
	if target == current:
		return current
	elif abs(target - current) <= VOLUME_CHANGE_STEP:
		return target
	elif current < target:
		return current + VOLUME_CHANGE_STEP
	elif current > target:
		return current - VOLUME_CHANGE_STEP

