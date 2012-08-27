import settings
import shutil
import os
from roundwared import roundexception

# Converts the given file to both wav and mp3 and stores the files in the audio directory.
# Handles files of various formats depending on the file extension.
def convert_uploaded_file (filename):
	(filename_prefix, filename_extension) = os.path.splitext(filename)
	upload_dir = get_upload_directory(filename_extension)
	filepath = os.path.join(upload_dir, filename)
	if not os.path.exists(filepath):
		raise roundexception.RoundException("Uploaded file not found: " + filepath)
	elif filename_extension == '.caf':
		convert_audio_file(upload_dir, filename_prefix, filename_extension, 'wav')
		convert_audio_file(settings.config["audio_dir"], filename_prefix, '.wav', 'mp3')
		return filename_prefix + '.wav'
	else:
		convert_audio_file(upload_dir, filename_prefix, filename_extension, 'wav')
		convert_audio_file(upload_dir, filename_prefix, filename_extension, 'mp3')
		return filename_prefix + '.wav'

# Converts the file to the given type, or copies it if it is the correct type.
def convert_audio_file(upload_dir, filename_prefix, filename_extension, dst_type):
	filepath = os.path.join(upload_dir, filename_prefix + filename_extension)
	if filename_extension == "." + dst_type:
		if not settings.config["audio_dir"] == upload_dir:
			shutil.copyfile(
				filepath,
				os.path.join(settings.config["audio_dir"], filename_prefix + filename_extension))
	else:
		if filename_extension == '.caf':
			os.system("/usr/bin/pacpl --to " + dst_type + " --outdir " + settings.config["audio_dir"] + " " + filepath + ">/dev/null")
		else: #if filename_extension in ffmpeg supported list
			os.system("/usr/bin/ffmpeg -y -i " + filepath + " " + os.path.join(settings.config["audio_dir"], filename_prefix + "." + dst_type) + " >/dev/null 2>/dev/null")

# Gets the directory the file is uploaded to by which extension it has.
def get_upload_directory (filename_extension):
	if filename_extension == '.flv':
		return settings.config["flv_upload_dir"]
	else:
		return settings.config["upload_dir"]

