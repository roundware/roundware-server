# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

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
