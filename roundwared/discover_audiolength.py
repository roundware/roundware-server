# Roundware Server is released under the GNU Lesser General Public License.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.conf import settings
import os
import subprocess
from roundwared import roundexception


def discover_and_set_audiolength(recording, filename):
    filepath = os.path.join(settings.AUDIO_DIR, filename)

    cmd = ['mediainfo', '--Inform=General;%Duration%', filepath]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, error = p.communicate()

    result = output.strip()

    if result:
        # TODO: Store audio length in millisecond.
        recording.audiolength = int(output) * 1000000
        recording.save()
    else:
        roundexception.RoundException("Recorded file is corrupt:" + filename)
