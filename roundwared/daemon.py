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


import os
import sys
import logging
logger = logging.getLogger(__name__)


def create_daemon(function, pidfile=False):
    # create - fork 1
    try:
        if os.fork() > 0:
            # os._exit(0) # exit father...
            sys.exit(0)
    except OSError, error:
        logger.critical('fork #1 failed: %d (%s)' % (error.errno, error.strerror))
        # os._exit(1)
        sys.exit(1)

    # it separates the son from the father
    # os.chdir('/') # Do this when I can run stream_script from $PATH
    os.setsid()
    os.umask(0)

    # create - fork 2
    try:
        pid = os.fork()
        if pid > 0:
            logger.debug('Daemon PID %d' % pid)
            if pidfile:
                pidfile = open(pidfile, "w")
                pidfile.write(str(pid) + "\n")
                pidfile.close()
            # os._exit(0)
            sys.exit(0)
    except OSError, error:
        logger.critical('fork #2 failed: %d (%s)' % (error.errno, error.strerror))
        # os._exit(1)
        sys.exit(1)

    function()
