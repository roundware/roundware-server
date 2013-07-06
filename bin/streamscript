#!/usr/bin/env python

import logging
import sys
import traceback
from roundwared import settings
from roundwared import daemon
from roundwared import roundgetopt
from roundwared.stream import RoundStream
from roundwared import rounddbus
# from memory_profiler import profile


def listofint(s):
	return map(int, s.split(','))

options_data = [
	#(name,			type,		default)
	("session_id",		int),
	("foreground",),
    ("project_id",		int,	0),
	#("subcategoryid",	listofint,	[]),
	#("questionid",		listofint,	[]),
	#("usertypeid",		listofint,	[]),
	#("genderid",		listofint,	[]),
	#("demographicid",       listofint,      []),
	#("ageid",		listofint,	[]),
	("configfile",		str),
	("latitude",		float,		False),
	("longitude",		float,		False),
	("audio_format",		str,		"MP3"),
        ("audio_stream_bitrate", int, 128),
]

# @profile
def main ():
	opts = roundgetopt.getopts(options_data)
	if opts.has_key('configfile'):
		settings.initialize_config(opts["configfile"])
	request = cmdline_opts_to_request(opts)
	initialize_logging(opts["foreground"])
	def thunk ():
		logging.debug("request is...")
		logging.debug (request)
		start_stream(opts["session_id"], opts["audio_format"], request)

	if opts["foreground"]:
		thunk()
	else:
		daemon.create_daemon(thunk, False)


def initialize_logging(foreground):
	FORMAT = '%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s'
	if foreground:
		logging.basicConfig(
			stream=sys.stdout,
			filemode="a",
			level=logging.DEBUG,
			format=FORMAT)
	else:
		logging.basicConfig(
			filename=settings.config["log_file"],
			filemode="a",
			level=logging.DEBUG,
			format=FORMAT)

def start_stream (sessionid, audio_format, request):
	try:
		logging.info("Starting stream " + str(sessionid))
		current_stream = RoundStream(
			sessionid, audio_format, request)
		rounddbus.add_stream_signal_receiver(current_stream)
		current_stream.start()
	except:
		logging.error(traceback.format_exc())

def cmdline_opts_to_request (opts):
	request = {}
#	for p in ['projectid', 'subcategoryid', 'questionid', 'usertypeid', 'genderid', 'demographicid', 'ageid', 'latitude', 'longitude']:
	for p in ['project_id', 'session_id','latitude', 'longitude', 'audio_stream_bitrate']:
		request[p] = opts[p]
	#logging.debug("cmdline_opts_to_request - session: " + str(request['session_id']))
	return request

main()
