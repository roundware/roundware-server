// Speaker Audio Upload Admin JavaScript
(function($) {
    'use strict';
    
    $(document).ready(function() {
        console.log('Speaker upload admin script loaded');
        
        // Find the audio file input
        var audioFileInput = $('#audio-file-input');
        var variantUrisTextarea = $('textarea[name="varianturis"]');
        
        console.log('Audio file input found:', audioFileInput.length);
        console.log('Variant URIs textarea found:', variantUrisTextarea.length);
        
        if (audioFileInput.length === 0) {
            console.error('Audio file input not found!');
            return;
        }
        
        // Create upload button
        var uploadButton = $('<button type="button" class="default" style="margin-top: 10px; margin-left: 10px;">Upload Audio File</button>');
        
        // Add button after the file input
        audioFileInput.after(uploadButton);
        console.log('Upload button added');
        
        // Handle file upload
        uploadButton.on('click', function() {
            var file = audioFileInput[0].files[0];
            if (!file) {
                alert('Please select an audio file first.');
                return;
            }
            
            // Show loading state
            uploadButton.prop('disabled', true).text('Uploading...');
            
            // Create FormData
            var formData = new FormData();
            formData.append('audio_file', file);
            
            // Get the current speaker ID from the URL
            var urlParts = window.location.pathname.split('/');
            var speakerId = null;
            
            // Look for the speaker ID in the URL pattern /admin/rw/speaker/{id}/change/
            for (var i = 0; i < urlParts.length; i++) {
                if (urlParts[i] === 'speaker' && i + 1 < urlParts.length) {
                    speakerId = urlParts[i + 1];
                    break;
                }
            }
            
            console.log('URL parts:', urlParts);
            console.log('Uploading to speaker ID:', speakerId);
            
            if (!speakerId) {
                alert('Could not determine speaker ID from URL');
                return;
            }
            
            // Make AJAX request
            $.ajax({
                url: '/admin/rw/speaker/' + speakerId + '/upload-audio/',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(data) {
                    console.log('Upload response:', data);
                    if (data.success) {
                        // Update the varianturis textarea
                        var currentUris = variantUrisTextarea.val().split('\n').filter(function(uri) {
                            return uri.trim();
                        });
                        currentUris.push(data.uri);
                        variantUrisTextarea.val(currentUris.join('\n'));
                        
                        // Clear the file input
                        audioFileInput.val('');
                        
                        // Show success message
                        alert('Audio file uploaded successfully! URI added to varianturis.');
                    } else {
                        alert('Upload failed: ' + data.error);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Upload error:', xhr.responseText);
                    var errorMsg = 'Upload failed: ' + error;
                    try {
                        var response = JSON.parse(xhr.responseText);
                        if (response.error) {
                            errorMsg = 'Upload failed: ' + response.error;
                        }
                    } catch (e) {
                        // Use default error message
                    }
                    alert(errorMsg);
                },
                complete: function() {
                    // Reset button state
                    uploadButton.prop('disabled', false).text('Upload Audio File');
                }
            });
        });
        
        // Simple fix: just make text dark
        var audioFileField = audioFileInput.closest('.form-row');
        if (audioFileField.length) {
            // Force text colors to be visible
            audioFileField.find('label').css({
                'color': '#000 !important',
                'font-weight': 'bold !important'
            });
            
            audioFileField.find('.help, .helptext').css({
                'color': '#333 !important',
                'font-style': 'italic !important'
            });
            
            // Make sure all text in the field is dark
            audioFileField.css('color', '#000 !important');
        }
    });
})(django.jQuery);
