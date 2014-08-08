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
from django.conf import settings
import shutil
import os
from roundwared import roundexception


# Converts the given file to both wav and mp3 and stores the files in the audio directory.
# Handles files of various formats depending on the file extension.
def convert_uploaded_file(filename):
    (filename_prefix, filename_extension) = os.path.splitext(filename)
    upload_dir = settings.MEDIA_ROOT
    filepath = os.path.join(upload_dir, filename)
    if not os.path.exists(filepath):
        raise roundexception.RoundException(
            "Uploaded file not found: " + filepath)
    elif filename_extension == '.caf':
        convert_audio_file(
            upload_dir, filename_prefix, filename_extension, 'wav')
        convert_audio_file(
            settings.MEDIA_ROOT, filename_prefix, '.wav', 'mp3')
        return filename_prefix + '.wav'
    else:
        convert_audio_file(
            upload_dir, filename_prefix, filename_extension, 'wav')
        convert_audio_file(
            upload_dir, filename_prefix, filename_extension, 'mp3')
        return filename_prefix + '.wav'


# Converts the file to the given type, or copies it if it is the correct type.
def convert_audio_file(upload_dir, filename_prefix, filename_extension, dst_type):
    filepath = os.path.join(upload_dir, filename_prefix + filename_extension)
    if filename_extension == "." + dst_type:
        if not settings.MEDIA_ROOT == upload_dir:
            shutil.copyfile(
                filepath,
                os.path.join(settings.MEDIA_ROOT, filename_prefix + filename_extension))
    else:
        if filename_extension == '.caf':
            os.system("/usr/bin/pacpl --to " + dst_type + " --outdir " +
                      settings.MEDIA_ROOT + " " + filepath + ">/dev/null")
        else: # if filename_extension in ffmpeg supported list
            os.system("/usr/bin/ffmpeg -y -i " + filepath + " " + os.path.join(settings.MEDIA_ROOT,
                      filename_prefix + "." + dst_type) + " >/dev/null 2>/dev/null")
