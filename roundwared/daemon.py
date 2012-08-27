import os
import sys
import logging

def create_daemon(function, pidfile = False):
	# create - fork 1
	try:
		if os.fork() > 0:
			#os._exit(0) # exit father...
			sys.exit(0)
	except OSError, error:
		logging.critical('fork #1 failed: %d (%s)' % (error.errno, error.strerror))
		#os._exit(1)
		sys.exit(1)

	# it separates the son from the father
	#os.chdir('/') # Do this when I can run stream_script from $PATH
	os.setsid()
	os.umask(0)

	# create - fork 2
	try:
		pid = os.fork()
		if pid > 0:
			logging.debug('Daemon PID %d' % pid)
			if pidfile:
				pidfile = open(pidfile,"w")
				pidfile.write(str(pid)+"\n")
				pidfile.close()
			#os._exit(0)
			sys.exit(0)
	except OSError, error:
		logging.critical('fork #2 failed: %d (%s)' % (error.errno, error.strerror))
		#os._exit(1)
		sys.exit(1)

	function()

