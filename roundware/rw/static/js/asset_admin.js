function hideMediaDisplay() {
    var media_display_section = $('div.form-row.media_display');
    $(media_display_section).each(function() {
        var display_div = $(this).find('div.media-display')[0];
        if (display_div.getAttribute('data-filename') == "None") {
            $(this).hide();
        }
        else {
            $(this).find('div.form-row.file').hide();
        }

    });
}

$(document).ready(function(){
    hideMediaDisplay();
});