#!/usr/bin/env python

import logging
import sys
import traceback

from roundwared import settings
from roundwared import daemon
from roundwared import roundgetopt
from roundwared.stream import RoundStream
from roundwared import rounddbus

def listofint(s):
    return map(int, s.split(','))

options_data = [
    ("session_id", int),
    ("foreground",),
    ("project_id", int, 0),
    ("configfile", str),
    ("latitude", float, False),
    ("longitude", float, False),
    ("audio_format", str, "MP3"),
    ("audio_stream_bitrate", int, 128),
]

logger = logging.getLogger(__name__)

# @profile
def main ():
    opts = roundgetopt.getopts(options_data)
    if opts.has_key('configfile'):
        settings.initialize_config(opts["configfile"])
    request = cmdline_opts_to_request(opts)
    def thunk ():
        logger.debug("request is...")
        logger.debug (request)
        start_stream(opts["session_id"], opts["audio_format"], request)

    if opts["foreground"]:
        thunk()
    else:
        daemon.create_daemon(thunk, False)

def start_stream (sessionid, audio_format, request):
    try:
        logger.info("Starting stream " + str(sessionid))
        current_stream = RoundStream(
            sessionid, audio_format, request)
        rounddbus.add_stream_signal_receiver(current_stream)
        current_stream.start()
    except:
        logger.error(traceback.format_exc())

def cmdline_opts_to_request (opts):
    request = {}
    for p in ['project_id', 'session_id','latitude', 'longitude', 'audio_stream_bitrate']:
        request[p] = opts[p]
    # logger.debug("cmdline_opts_to_request - session: " + str(request['session_id']))
    return request

main()
