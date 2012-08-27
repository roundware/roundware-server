import configobj
import validate
import StringIO
import os
from roundwared import roundexception

configdir = "/etc/roundware"
default_configfile = "/etc/roundwared"
configstring = """
	icecast_port		= integer(1, 65535, default=8000)
	icecast_host		= string(default=localhost)
	icecast_username	= string(default=admin)
	icecast_password	= string(default=roundice)
	icecast_source_username	= string(default=source)
	icecast_source_password	= string(default=roundice)
	audio_dir		= string(default=/home/halsey/round/audio)
	upload_dir		= string(default=/var/www/reconaudio)
	flv_upload_dir		= string(default=/usr/lib/red5/webapps/oflaDemo/streams)
	log_file		= string(default=/var/log/roundware)
	dbuser			= string(default=round)
	dbpasswd		= string(default=round)
	dbname			= string(default=round)
	num_pan_steps		= integer(1, default=200) # discreate steps
	stereo_pan_interval	= integer(1, default=10) # milliseconds
	ping_interval		= integer(1, default=10000) # milliseconds
	master_volume		= float(0.0, default=3)
	stream_caps		= string(default="audio/x-raw-int,rate=44100,channels=2,width=16,depth=16,signed=(boolean)true")
	heartbeat_timeout	= integer(1, 3600, default=30)
	recording_repeat_count	= integer(0, default = 2)
	recording_radius	= integer(0, 6378100, default=16)
"""

# String -> ConfigObj
# Returns the configobj created by reading from the given filename or using defaults where necessary.
def read_configfile (filename):
	configspec = StringIO.StringIO(configstring)
	tmpconfig = configobj.ConfigObj(filename, configspec = configspec)
	if not tmpconfig.validate(validate.Validator(), copy = True):
		raise roundexception.RoundException("Invalid config file")
	return tmpconfig

# String -> None
# Reads a configobj from a given filename and assigns the global config variable to that config.
def initialize_config (filename):
	global config
	if os.access(filename, os.F_OK):
		config = False
		config = read_configfile(filename)
	else:
		raise roundexception.RoundException("Config file not found")

# Read in the default config file, store it in config (to be referenced by other modules)
config = read_configfile(default_configfile)

# If there is no existing config at the default location, write one out if there is write permission.
(dir, relativefilename) = os.path.split(default_configfile)
if (os.access(default_configfile, os.F_OK) and os.access(default_configfile, os.W_OK)) \
	or (not os.access(default_configfile, os.F_OK) and os.access(dir, os.W_OK)):
	config.write()

# mode is compressor or expander
# characteristics is "hard-knee" (default) or "soft-knee" (smooth). Default="hard-knee"
# ratio is a floating point number between 0 and infinity, Default=1
# threshold is a floating point number between 0 and 1, Default=0
RECORDING_AUDIO_DYNAMICS = [
	{
		"mode" : "compressor",
		"characteristics" : "hard-knee",
		"ratio" : 0.001,
		"threshold" : 0.05,
		"amplification" : 4,
	},
]

