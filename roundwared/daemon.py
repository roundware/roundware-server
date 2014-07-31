# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
import os
import sys
import logging
logger = logging.getLogger(__name__)


def create_daemon(function):
    # create - fork 1
    try:
        if os.fork() > 0:
            # os._exit(0) # exit father...
            sys.exit(0)
    except OSError, error:
        logger.critical('fork #1 failed: %d (%s)' %
                        (error.errno, error.strerror))
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
            sys.exit(0)
    except OSError, error:
        logger.critical('fork #2 failed: %d (%s)' %
                        (error.errno, error.strerror))
        sys.exit(1)

    function()
