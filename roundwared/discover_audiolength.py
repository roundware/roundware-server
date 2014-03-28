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
# along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.html>.

#***********************************************************************************#


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


def discover_and_set_audiolength(recording, filename):
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
