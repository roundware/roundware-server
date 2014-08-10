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
# along with this program.  If not, see
# <http://www.gnu.org/licenses/lgpl.html>.

#***********************************************************************************#


from __future__ import unicode_literals
import os
import logging


logger = logging.getLogger(__name__)

def create_daemon(function):
    """
    Convert rwstreamd.py to a console-less daemon.
    """

    try:
        # Create the first child process.
        pid = os.fork()
    except OSError, error:
        logger.critical('First Child fork failed: %d (%s)' %
                        (error.errno, error.strerror))
        os._exit(1)

    # Exit the parent process to return the control to the shell.
    if pid is not 0:
        os._exit(0)

    # Become the session leader
    os.setsid()

    try:
        # Create the second child process, AKA grandchild.
        pid = os.fork()
    except OSError, error:
        logger.critical('fork #2 failed: %d (%s)' %
                        (error.errno, error.strerror))
        os._exit(1)

    # Exit the first child process to stop zombies
    if pid is not 0:
        # TODO: If we ever want to track daemon PIDs, they are available here.
        logger.debug('Daemon PID %d' % pid)
        os._exit(0)

    # Set the working directory to /
    os.chdir('/')
    # Reset the process umask
    os.umask(0)

    # Call the original function
    function()
