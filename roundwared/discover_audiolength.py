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


from roundware import settings
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
