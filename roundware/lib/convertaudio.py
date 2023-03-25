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


# Converts the file to the given type even if same type (e.g. mp3->mp3) in order
# to ensure proper sample rate of 48KHz which is required by iOS Safari
def convert_audio_file(upload_dir, filename_prefix, filename_extension, dst_type):
    filepath = os.path.join(upload_dir, filename_prefix + filename_extension)
    if dst_type == "wav":
        output_filepath = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}.{dst_type}")
        ffmpeg.input(filepath).output(output_filepath).run()
    elif dst_type == "mp3":
        output_filepath = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}.{dst_type}")
        output_filepath_temp = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}-temp.{dst_type}")
        ffmpeg.input(filepath).output(output_filepath_temp, acodec='libmp3lame', ar=48000).run()
        os.rename(output_filepath_temp, output_filepath)
    elif dst_type == "m4a":
        output_filepath = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}.{dst_type}")
        output_filepath_temp = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}-temp.{dst_type}")
        ffmpeg.input(filepath).output(output_filepath_temp, acodec='aac', ar=48000).run()
        os.rename(output_filepath_temp, output_filepath)
