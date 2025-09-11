"""
Advanced admin features for Speaker varianturis with file upload capability.
This is an optional enhancement that would require additional setup.
"""

from django import forms
from django.contrib import admin
from django.core.files.storage import default_storage
from django.conf import settings
import os
import uuid
from datetime import datetime


class SpeakerUploadForm(forms.ModelForm):
    """
    Enhanced form with file upload capability for variant URIs.
    This would require additional JavaScript and file handling.
    """
    
    # File upload field for new audio files
    audio_upload = forms.FileField(
        required=False,
        help_text="Upload a new audio file to add to variant URIs",
        widget=forms.FileInput(attrs={
            'accept': 'audio/*',
            'class': 'audio-upload-input'
        })
    )
    
    class Meta:
        model = Speaker
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom fields for managing variant URIs
        self.fields['varianturis'] = forms.CharField(
            widget=forms.Textarea(attrs={
                'rows': 5,
                'cols': 80,
                'placeholder': 'Enter one URI per line...'
            }),
            help_text="Enter one URI per line. Uploaded files will be added automatically."
        )
    
    def clean_varianturis(self):
        """Convert textarea input to list format."""
        value = self.cleaned_data.get('varianturis', '')
        if not value:
            return []
        
        uris = [uri.strip() for uri in value.split('\n') if uri.strip()]
        return uris
    
    def clean_audio_upload(self):
        """Handle audio file upload and generate URI."""
        uploaded_file = self.cleaned_data.get('audio_upload')
        if not uploaded_file:
            return None
        
        # Validate file type
        allowed_types = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp3']
        if uploaded_file.content_type not in allowed_types:
            raise forms.ValidationError("Please upload a valid audio file (MP3, WAV, OGG)")
        
        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"speaker_audio_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
        
        # Save file to media directory
        file_path = os.path.join('speaker_audio', unique_filename)
        saved_path = default_storage.save(file_path, uploaded_file)
        
        # Generate full URL
        base_url = getattr(settings, 'MEDIA_URL', '/media/')
        if not base_url.endswith('/'):
            base_url += '/'
        
        full_url = f"{base_url}{saved_path}"
        return full_url
    
    def save(self, commit=True):
        """Save the form and handle uploaded files."""
        instance = super().save(commit=False)
        
        # Get uploaded file URL
        uploaded_url = self.clean_audio_upload()
        
        # Add uploaded URL to varianturis if provided
        if uploaded_url:
            current_uris = instance.varianturis or []
            if uploaded_url not in current_uris:
                current_uris.append(uploaded_url)
                instance.varianturis = current_uris
        
        if commit:
            instance.save()
        
        return instance


# JavaScript for enhanced admin interface
ADMIN_JS = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Add file upload functionality
    const audioUpload = document.querySelector('.audio-upload-input');
    const varianturisTextarea = document.querySelector('textarea[name="varianturis"]');
    
    if (audioUpload && varianturisTextarea) {
        audioUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Show upload progress
                const progressDiv = document.createElement('div');
                progressDiv.innerHTML = '<p>Uploading: ' + file.name + '</p>';
                progressDiv.className = 'upload-progress';
                varianturisTextarea.parentNode.appendChild(progressDiv);
                
                // In a real implementation, you'd use AJAX to upload the file
                // and then add the resulting URL to the textarea
                console.log('File selected for upload:', file.name);
            }
        });
    }
});
</script>
"""

# CSS for enhanced admin interface
ADMIN_CSS = """
<style>
.upload-progress {
    background: #e7f3ff;
    border: 1px solid #b3d9ff;
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
}

.audio-upload-input {
    margin: 10px 0;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.variant-uris-container {
    margin: 10px 0;
}

.variant-uris-container textarea {
    width: 100%;
    max-width: 600px;
    font-family: monospace;
    font-size: 12px;
    line-height: 1.4;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 8px;
}
</style>
"""
