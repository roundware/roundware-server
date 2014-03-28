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


import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import json

INTERFACE = "org.roundware.StreamScript"
OBJECT_PATH = "/org/roundware/StreamScript/emitter"


def add_stream_signal_receiver(stream):
    def handler(sessionid, operation, args):
        if stream.sessionid == sessionid:
            if operation == "modify_stream":
                request = json.loads(args)
                stream.modify_stream(request)
            elif operation == "move_listener":
                request = json.loads(args)
                stream.move_listener(request)
            elif operation == "heartbeat":
                stream.heartbeat()
            elif operation == "skip_ahead":
                stream.skip_ahead()
            elif operation == "play_asset":
                request = json.loads(args)
                stream.play_asset(request)
        else:
            if operation == "refresh_recordings":
                stream.refresh_recordings()

    bus = dbus.SystemBus(mainloop=DBusGMainLoop())
    signal_match = bus.add_signal_receiver(handler, signal_name="round_stream_control")
    return signal_match


def emit_stream_signal(sessionid, operation, args):
    global_emitter.round_stream_control(sessionid, operation, args)


class StreamSignalEmmiter(dbus.service.Object):
    global INTERFACE
    global OBJECT_PATH

    def __init__(self):
        bus = dbus.SystemBus(mainloop=DBusGMainLoop())
        dbus.service.Object.__init__(self, bus, OBJECT_PATH)

    @dbus.service.signal(dbus_interface=INTERFACE, signature='iss')
    def round_stream_control(self, sessionid, operation, args): pass

global_emitter = StreamSignalEmmiter()
