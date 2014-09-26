#!/usr/bin/env python

from __future__ import unicode_literals
import logging
import traceback

from roundwared import daemon
from roundwared.stream import RoundStream
from roundwared import rounddbus
import getopt
import sys
import re


def listofint(s):
    return map(int, s.split(','))

options_data = [
    ("session_id", int),
    ("foreground",),
    ("project_id", int, 0),
    ("latitude", float, False),
    ("longitude", float, False),
    ("audio_format", str, "MP3"),
    ("audio_stream_bitrate", int, 128),
]

# Set specifically since __name__ is __main__
logger = logging.getLogger('roundwared.rwstreamd')


def main():
    opts = getopts(options_data)
    request = cmdline_opts_to_request(opts)

    def thunk():
        logger.debug(request)
        start_stream(opts["session_id"], opts["audio_format"], request)

    if opts["foreground"]:
        thunk()
    else:
        daemon.create_daemon(thunk)


def start_stream(sessionid, audio_format, request):
    try:
        logger.info("Starting stream " + str(sessionid))
        current_stream = RoundStream(
            sessionid, audio_format, request)
        rounddbus.add_stream_signal_receiver(current_stream)
        current_stream.start()
    except:
        logger.error(traceback.format_exc())


def cmdline_opts_to_request(opts):
    request = {}
    for p in ['project_id', 'session_id', 'latitude', 'longitude', 'audio_stream_bitrate']:
        request[p] = opts[p]
    # logger.debug("cmdline_opts_to_request - session: " + str(request['session_id']))
    return request

def getopts(options):

    optargs = {}
    opttype = {}
    validopts = ["help"]

    for o in options:
        if len(o) == 1:
            name = o[0]
            optargs[name] = False
            validopts.append(name)
        elif len(o) in (2, 3):
            name = o[0]
            type = o[1]
            validopts.append(name + "=")
            opttype[name] = type
            if len(o) == 3:
                default = o[2]
                optargs[name] = default
        else:
            print "Invalid opt argument: ", o
            sys.exit(2)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", validopts)
    except getopt.GetoptError, err:
        print str(err)
        usage(validopts)
        sys.exit(2)

    regexp = re.compile('^--')

    for o, a in opts:
        if o == "--help":
            usage()
            sys.exit()
        else:
            p = regexp.sub('', o)
            if p in opttype.keys():
                optargs[p] = opttype[p](a)
            else:
                optargs[p] = True

    return optargs


def usage(validopts):
    # TODO: A better error message should be written for this
    print "Invalid arguments."
    sys.exit(2)


if  __name__ == '__main__':
    main()
