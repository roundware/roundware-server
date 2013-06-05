$(document).ready(function(){
    var media_display = $('div.media-display');
    var media_display_section = $('div.form-row.media_display');

    var file_upload_section = $('div.form-row.file');

    if ( media_display.attr('data-filename') == "None" ) {
        media_display_section.hide();
    } else {
        file_upload_section.hide();
    }
});