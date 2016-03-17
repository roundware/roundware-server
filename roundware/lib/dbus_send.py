# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# Sends dbus signals to rwstreamd.py
from __future__ import unicode_literals
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

INTERFACE = "org.roundware.StreamScript"
OBJECT_PATH = "/org/roundware/StreamScript/emitter"

def emit_stream_signal(sessionid, operation, args):
    global_emitter.round_stream_control(sessionid, operation, args)


class StreamSignalEmmiter(dbus.service.Object):
    global INTERFACE
    global OBJECT_PATH

    def __init__(self):
        bus = dbus.SystemBus(mainloop=DBusGMainLoop())
        dbus.service.Object.__init__(self, bus, OBJECT_PATH)

    @dbus.service.signal(dbus_interface=INTERFACE, signature='iss')
    def round_stream_control(self, sessionid, operation, args):
        pass

global_emitter = StreamSignalEmmiter()
