# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

import os
import uuid
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def handle_speaker_audio_upload(uploaded_file, speaker, request=None, project_id=None):
    """
    Handle uploaded audio file for a speaker and return the full URI.
    
    Args:
        uploaded_file: Django UploadedFile object
        speaker: Speaker instance
        request: Django request object (optional, used to build full URL)
        project_id: Project ID for naming (optional, will use speaker.project.id if not provided)
    
    Returns:
        str: The full URI for the uploaded file
    """
    # Get project ID
    if project_id is None:
        project_id = speaker.project.id if speaker.project else 1
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Create filename following the existing pattern: speaker-project{id}-{code}-{timestamp}.{ext}
    speaker_code = speaker.code or 'unknown'
    filename = f"speaker-project{project_id}-{speaker_code}-{timestamp}{file_extension}"
    
    # Ensure the file extension is valid for audio
    if file_extension not in ['.mp3', '.wav', '.m4a', '.aac', '.ogg']:
        # Default to .mp3 if extension is not recognized
        filename = f"speaker-project{project_id}-{speaker_code}-{timestamp}.mp3"
    
    # Create the full path
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save the file
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    # Process the uploaded file (compression, normalization, format conversion)
    try:
        from roundware.lib.convertaudio import convert_uploaded_file
        processed_filename = convert_uploaded_file(filename)
        # Update filename to the processed version (MP3)
        filename = processed_filename
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
    except Exception as e:
        # Log the error but don't fail the upload
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Audio processing failed for {filename}: {e}")
        # Continue with original file if processing fails
    
    # Build the full URI
    media_path = os.path.join(settings.MEDIA_URL, filename).replace('\\', '/')
    
    # If we have a request object, build the full URL
    if request:
        # Use the request's scheme and host to build the full URL
        scheme = request.scheme
        host = request.get_host()
        return f"{scheme}://{host}{media_path}"
    else:
        # Fallback: try to use settings if available
        if hasattr(settings, 'SITE_URL'):
            return f"{settings.SITE_URL}{media_path}"
        else:
            # Return just the media path (relative URL)
            return media_path


def validate_audio_file(uploaded_file):
    """
    Validate that the uploaded file is a valid audio file.
    
    Args:
        uploaded_file: Django UploadedFile object
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    if uploaded_file.size > max_size:
        return False, f"File too large. Maximum size is {max_size // (1024*1024)}MB"
    
    # Check file extension
    allowed_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension not in allowed_extensions:
        return False, f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
    
    # Check MIME type if available
    if hasattr(uploaded_file, 'content_type'):
        allowed_mime_types = [
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/x-wav',
            'audio/mp4', 'audio/mp4a-latm', 'audio/aac', 'audio/ogg',
            'audio/flac', 'audio/x-caf'
        ]
        
        if uploaded_file.content_type not in allowed_mime_types:
            return False, f"Invalid MIME type: {uploaded_file.content_type}"
    
    return True, None
