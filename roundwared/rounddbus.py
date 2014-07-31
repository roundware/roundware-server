# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
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
    signal_match = bus.add_signal_receiver(
        handler, signal_name="round_stream_control")
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
    def round_stream_control(self, sessionid, operation, args):
        pass

global_emitter = StreamSignalEmmiter()
