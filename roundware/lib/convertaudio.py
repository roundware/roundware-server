# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.conf import settings
import shutil
import os
from pathlib import Path
import ffmpeg
from .exception import RoundException


# Converts the given file to both wav and mp3 and stores the files in the audio directory.
# Handles files of various formats depending on the file extension.
def convert_uploaded_file(filename):
    (filename_prefix, filename_extension) = os.path.splitext(filename)
    upload_dir = settings.MEDIA_ROOT
    filepath = os.path.join(upload_dir, filename)
    if not os.path.exists(filepath):
        raise RoundException(
            "Uploaded file not found: " + filepath)
    else:
        convert_audio_file(
            upload_dir, filename_prefix, filename_extension, 'm4a')
        convert_audio_file(
            upload_dir, filename_prefix, filename_extension, 'mp3')
        filename_path = Path(filepath)
        filename_wav = filename_path.with_suffix('.wav')
        if os.path.exists(filename_wav):
            os.remove(filename_wav)
        else:
            print("wav version of file does not exist for deletion")
        return filename_prefix + '.mp3'


# Converts the file to the given type, or copies it if it is the correct type.
def convert_audio_file(upload_dir, filename_prefix, filename_extension, dst_type):
    filepath = os.path.join(upload_dir, filename_prefix + filename_extension)
    if filename_extension == "." + dst_type:
        if not settings.MEDIA_ROOT == upload_dir:
            shutil.copyfile(
                filepath,
                os.path.join(settings.MEDIA_ROOT, filename_prefix + filename_extension))
    else:
        if dst_type == "wav":
            output_filepath = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}.{dst_type}")
            ffmpeg.input(filepath).output(output_filepath).run()
        elif dst_type == "mp3":
            output_filepath = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}.{dst_type}")
            ffmpeg.input(filepath).output(output_filepath, acodec='libmp3lame').run()
        elif dst_type == "m4a":
            output_filepath = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}.{dst_type}")
            ffmpeg.input(filepath).output(output_filepath, acodec='aac').run()
