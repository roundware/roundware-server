# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from __future__ import unicode_literals
from django.conf import settings
import shutil
import os
import logging
from pathlib import Path
import ffmpeg
from .exception import RoundException

logger = logging.getLogger(__name__)


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
        # Apply audio compression if enabled in settings (before normalization)
        if getattr(settings, 'AUDIO_COMPRESSION_ENABLED', True):
            logger.info(f"Audio compression enabled - processing {filename}")
            compress_audio_file(upload_dir, filename_prefix, filename_extension)
        else:
            logger.debug(f"Audio compression disabled - skipping {filename}")
        
        # Normalize audio if enabled in settings (after compression)
        if getattr(settings, 'AUDIO_NORMALIZATION_ENABLED', True):
            logger.info(f"Audio normalization enabled - processing {filename}")
            normalize_audio_file(upload_dir, filename_prefix, filename_extension)
        else:
            logger.debug(f"Audio normalization disabled - skipping {filename}")
        
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


def normalize_audio_file(upload_dir, filename_prefix, filename_extension):
    """
    Normalize audio file to target LUFS level using ffmpeg.
    Only normalizes if the current LUFS is outside the tolerance range.
    """
    filepath = os.path.join(upload_dir, filename_prefix + filename_extension)
    
    # Get target LUFS and tolerance from settings
    target_lufs = getattr(settings, 'AUDIO_NORMALIZATION_TARGET_LUFS', -23.0)
    tolerance = getattr(settings, 'AUDIO_NORMALIZATION_TOLERANCE', 2.0)
    
    try:
        # First, measure the current LUFS of the file
        probe = ffmpeg.probe(filepath)
        if not probe or 'streams' not in probe:
            logger.warning(f"Could not probe audio file: {filepath}")
            return
        
        # Find audio stream
        audio_stream = None
        for stream in probe['streams']:
            if stream['codec_type'] == 'audio':
                audio_stream = stream
                break
        
        if not audio_stream:
            logger.warning(f"No audio stream found in file: {filepath}")
            return
        
        # Use ffmpeg to measure LUFS (Loudness Units relative to Full Scale)
        try:
            # Run ffmpeg to measure LUFS using ebur128 filter
            # This approach directly measures the integrated loudness
            cmd = [
                'ffmpeg', '-i', filepath, '-af', 'ebur128=peak=true:dualmono=true',
                '-f', 'null', '-'
            ]
            
            import subprocess
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            current_lufs = None
            
            # Parse the LUFS measurement from stderr
            for line in result.stderr.split('\n'):
                if 'I:' in line and 'LUFS' in line:
                    # Extract the LUFS value
                    try:
                        # Look for pattern like "I: -23.4 LUFS"
                        parts = line.split('I:')
                        if len(parts) > 1:
                            lufs_part = parts[1].split('LUFS')[0].strip()
                            current_lufs = float(lufs_part)
                            break
                    except (ValueError, IndexError):
                        continue
            
            if current_lufs is None:
                logger.warning(f"Could not measure LUFS for file: {filepath}")
                logger.debug(f"FFmpeg stderr: {result.stderr}")
                return
            
            logger.info(f"Audio normalization check - File: {os.path.basename(filepath)}, Current LUFS: {current_lufs}, Target: {target_lufs}, Tolerance: {tolerance}")
            
            # Check if normalization is needed
            if abs(current_lufs - target_lufs) <= tolerance:
                logger.info(f"Audio file {os.path.basename(filepath)} is within tolerance range, skipping normalization")
                return
            
            # Apply normalization using ffmpeg loudnorm filter
            temp_normalized_file = os.path.join(upload_dir, f"{filename_prefix}-normalized-temp{filename_extension}")
            
            # Use the loudnorm filter for proper loudness normalization
            # This is more reliable than manual gain adjustment
            normalize_cmd = [
                'ffmpeg', '-i', filepath,
                '-af', f'loudnorm=I={target_lufs}:LRA=11:TP=-1.0',
                '-ar', '44100',  # Preserve original sample rate
                '-y',  # Overwrite output file
                temp_normalized_file
            ]
            
            # For compressed formats, we need to re-encode
            if filename_extension.lower() in ['.mp3']:
                normalize_cmd = [
                    'ffmpeg', '-i', filepath,
                    '-af', f'loudnorm=I={target_lufs}:LRA=11:TP=-1.0',
                    '-acodec', 'libmp3lame', '-ar', '48000',
                    '-y',
                    temp_normalized_file
                ]
            elif filename_extension.lower() in ['.m4a', '.aac']:
                normalize_cmd = [
                    'ffmpeg', '-i', filepath,
                    '-af', f'loudnorm=I={target_lufs}:LRA=11:TP=-1.0',
                    '-acodec', 'aac', '-ar', '48000',
                    '-y',
                    temp_normalized_file
                ]
            
            result = subprocess.run(normalize_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(temp_normalized_file):
                # Replace the original file with the normalized version
                os.replace(temp_normalized_file, filepath)
                logger.info(f"Successfully normalized {os.path.basename(filepath)} from {current_lufs} LUFS to target {target_lufs} LUFS")
            else:
                logger.error(f"Normalization failed for {os.path.basename(filepath)}")
                logger.debug(f"FFmpeg stderr: {result.stderr}")
                # Clean up temp file if it exists
                if os.path.exists(temp_normalized_file):
                    os.remove(temp_normalized_file)
                return
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout during normalization of {os.path.basename(filepath)}")
            return
        except Exception as e:
            logger.warning(f"Error during LUFS measurement: {e}")
            # Fallback to simple gain adjustment if LUFS measurement fails
            try:
                temp_normalized_file = os.path.join(upload_dir, f"{filename_prefix}-normalized-temp{filename_extension}")
                
                # Apply a conservative gain adjustment
                fallback_cmd = [
                    'ffmpeg', '-i', filepath,
                    '-af', 'volume=0.8',  # Reduce volume by 20% as a safe default
                    '-y',
                    temp_normalized_file
                ]
                
                result = subprocess.run(fallback_cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(temp_normalized_file):
                    os.replace(temp_normalized_file, filepath)
                    logger.info(f"Applied fallback normalization to {os.path.basename(filepath)}")
                else:
                    logger.error(f"Fallback normalization failed: {result.stderr}")
                    if os.path.exists(temp_normalized_file):
                        os.remove(temp_normalized_file)
                
            except Exception as fallback_error:
                logger.error(f"Fallback normalization also failed: {fallback_error}")
                return
                
    except Exception as e:
        logger.error(f"Error normalizing audio file {os.path.basename(filepath)}: {e}")
        return


def compress_audio_file(upload_dir, filename_prefix, filename_extension):
    """
    Apply aggressive audio compression to flatten dynamics using ffmpeg.
    Uses acompressor filter with configurable settings for aggressive compression.
    """
    filepath = os.path.join(upload_dir, filename_prefix + filename_extension)
    
    # Get compression settings from Django settings
    ratio = getattr(settings, 'AUDIO_COMPRESSION_RATIO', 4.0)
    threshold = getattr(settings, 'AUDIO_COMPRESSION_THRESHOLD', -12.0)
    attack = getattr(settings, 'AUDIO_COMPRESSION_ATTACK', 5)
    release = getattr(settings, 'AUDIO_COMPRESSION_RELEASE', 50)
    makeup_gain = getattr(settings, 'AUDIO_COMPRESSION_MAKEUP_GAIN', 2.0)
    
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            logger.warning(f"File not found for compression: {filepath}")
            return
        
        # Create temporary compressed file
        temp_compressed_file = os.path.join(upload_dir, f"{filename_prefix}-compressed-temp{filename_extension}")
        
        # Build compression filter string
        # Using acompressor filter for aggressive compression
        # ratio: compression ratio (higher = more aggressive)
        # threshold: level above which compression kicks in (in dB)
        # attack: how quickly compression responds (in ms)
        # release: how quickly compression releases (in ms)
        # makeup: gain compensation after compression (in dB)
        compression_filter = (
            f"acompressor=ratio={ratio}:threshold={threshold}dB:"
            f"attack={attack}:release={release}:makeup={makeup_gain}dB"
        )
        
        # Build ffmpeg command for compression
        compress_cmd = [
            'ffmpeg', '-i', filepath,
            '-af', compression_filter,
            '-ar', '44100',  # Preserve original sample rate
            '-y',  # Overwrite output file
            temp_compressed_file
        ]
        
        # For compressed formats, we need to re-encode
        if filename_extension.lower() in ['.mp3']:
            compress_cmd = [
                'ffmpeg', '-i', filepath,
                '-af', compression_filter,
                '-acodec', 'libmp3lame', '-ar', '48000',
                '-y',
                temp_compressed_file
            ]
        elif filename_extension.lower() in ['.m4a', '.aac']:
            compress_cmd = [
                'ffmpeg', '-i', filepath,
                '-af', compression_filter,
                '-acodec', 'aac', '-ar', '48000',
                '-y',
                temp_compressed_file
            ]
        
        logger.info(f"Applying audio compression - File: {os.path.basename(filepath)}, "
                   f"Ratio: {ratio}, Threshold: {threshold}dB, Attack: {attack}ms, "
                   f"Release: {release}ms, Makeup: {makeup_gain}dB")
        
        # Run compression
        import subprocess
        result = subprocess.run(compress_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(temp_compressed_file):
            # Replace the original file with the compressed version
            os.replace(temp_compressed_file, filepath)
            logger.info(f"Successfully compressed {os.path.basename(filepath)} with aggressive settings")
        else:
            logger.error(f"Compression failed for {os.path.basename(filepath)}")
            logger.debug(f"FFmpeg stderr: {result.stderr}")
            # Clean up temp file if it exists
            if os.path.exists(temp_compressed_file):
                os.remove(temp_compressed_file)
            return
            
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout during compression of {os.path.basename(filepath)}")
        return
    except Exception as e:
        logger.error(f"Error during audio compression: {e}")
        return
