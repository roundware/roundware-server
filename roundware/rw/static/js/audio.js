/**
 * Creates the initial jplayer instance to be copied into all .audio-file divs.
 * @param id
 */
var jpCreator = function(id) { return '<div id="jquery_jplayer_' + id + '" class="jp-jplayer"></div>' +

    '<div id="jp_container_' + id + '" class="jp-audio">' +
    '<div class="jp-type-single">' +
        '<div class="jp-gui jp-interface">' +
            '<ul class="jp-controls">' +


                '<li><a href="javascript:;" class="jp-play" tabindex="1">play</a></li>'+
                //'<li><a href="javascript:;" class="jp-pause" tabindex="1">pause</a></li>'+
                '<li><a href="javascript:;" class="jp-stop" tabindex="1">stop</a></li>'+
            '</ul>'+

        '<div class="jp-no-solution">'+
            '<span>Update Required</span>'+
        'To play the media you will need to either update your browser to a recent version or update your <a href="http://get.adobe.com/flashplayer/" target="_blank">Flash plugin</a>.'+
        '</div>'+
    '</div>'+
    '</div>';
};


/**
 * Initializes jplayer on the given dom element.
 * @param id
 * @param {string} filename Audio file to be played. The extention will be parsed
 * in order to initialize jPlayer with the correct media player.
 * @param dom A copy of the dom element created with jpCreator
 * @param $ jQuery, passed in to avoid namespacing conflicts.
 */
function createPlayer(id, filename, dom, $) {
    var re = /.*\.(.{3,4})$/; // File extention = last 3-4 chars after last period.
    var extension = filename.match(re)[1];
    if (!extension) {
        console.log("Invalid or missing file extention");
        return;
    }
    var setMediaObject = {};
    setMediaObject[extension] = AUDIO_FILE_SERVER + filename;

    $(dom).jPlayer({
        preload: 'none',
        ready: function() {
            $(this).jPlayer("setMedia", setMediaObject);
        },
        cssSelectorAncestor: "#jp_container_" + id,
        swfPath: "/static/js",
        supplied: extension
    });
}

(function($) {
    var filename;
    var id = 1;

    $(document).ready( function() {
        var baseJplayer = $(jpCreator(''));
        // If we are in the change_list view, this will update every row with a jplayer instance
        // If we are in the singular change view, this will only create one jplayer instance
        $('div.audio-file').each( function() {
            var that = this;
            var dom = baseJplayer.clone();
            // Create identifiers to tie buttons to <audio> elements.
            dom[0].id = 'jquery_jplayer_' + id;
            dom[1].id = 'jp_container_' + id;
            filename = $(this).attr('data-filename');
            $(that).append(dom);
            createPlayer(id, filename, dom[0], $);
            id++;
        });
    })

}(django.jQuery));