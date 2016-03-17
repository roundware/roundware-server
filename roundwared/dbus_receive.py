# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

# Receives dbus signals from roundware/lib/server.py
from __future__ import unicode_literals
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import json


def add_signal_receiver(stream):
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
