import settings
import logging
import os
import threading
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
from gst.extend import discoverer
from roundwared import db
from roundwared import roundexception
from roundware.rw import models
#FIXME: Is using a main loop really the only way to get this to work? Doesn't seem like
# this function is safe to me. It might have weird interactions if called in a program that
# has its own main_loop
def discover_and_set_audiolength (recording, filename):
	main_loop = gobject.MainLoop()
	def discovered(d, is_media):
		if is_media:
			recording.audiolength = d.audiolength
			recording.save()
			#db.update_audiolength(filename, d.audiolength)
			main_loop.quit()
		else:
			roundexception.RoundException("Recorded file is corrupt:" + filename)
	d = discoverer.Discoverer(os.path.join(settings.config["audio_dir"], filename))
	d.connect('discovered', discovered)
	d.discover()
	main_loop.run()

