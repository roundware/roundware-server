$(document).ready(function(){
    var audio_player = $('div.audio-file');
    var audio_player_section = $('div.form-row.audio_player');

    var file_upload_section = $('div.form-row.file');

    if ( audio_player.attr('data-filename') == "None" ) {
        audio_player_section.hide();
    } else {
        file_upload_section.hide();
    }
});