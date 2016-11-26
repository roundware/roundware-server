// make sure we have a valid namespace
if (!Roundware) {
    var Roundware = function () {
    };
}

/**
 * The Roundware.ListenMap constructor returns an object with a single public function
 * (main) which is in turn called with a project ID and a Google Map for plotting
 * recordings.
 *
 * The public callback to main iterates over the functions specified by RW.workflow
 * to grab a projects config, tags, and assets from the Roundware server, display
 * recordings on the map and tags as a list of filters, and then adds event listeners
 * to UI elements to allow you to listen to and modify the audio stream.
 *
 * Project tags are displayed as a list of checkboxes which can be toggled on/off
 * to show/hide recordings on the map and to modify the stream. Moving the listening
 * pin will also cause the stream to be modified based on its new lat/lng.
 *
 * @author Zak Burke, zak.burke@gmail.com
 *
 *
 */
Roundware.ListenMap = function (opts) {
    var options = $.extend({}, {
        url: 'http://roundware.dyndns.org/api/1/',
    }, opts);


    var project_id = null;

    var config = {};
    var tags = null;
    var assets = null;
    var map = null;
    var all_assets = [];
    var iOSdevice = false;
    var is_listening = false;

    var listening_pin = null;

    // ordered lists of methods to be called in series
    var workflow = [
        get_config,
        get_tags,
        get_assets,
        map_assets,
        map_speakers,
        add_listening_pin,
        show_filters,
        show_listening_button
    ];
    //var workflow = [get_config, get_tags, get_assets, map_assets, show_filters]; // no speaker mapping


    /**
     * cache the input parameters, then grab data from RW and display filters and
     * map of recordings, speakers, and a listening pin. The workhorse here is
     * main_callback(), which loops through the methods of RW.workflow to retrieve
     * the data and display it.
     *
     * @param string m_url: URL of the roundware server, e.g. http://roundware.dyndns.org/api/1/
     * @param int m_project_id: project PK on the Roundware server
     * @param google.maps.Map m_map: a Google Map
     */
    this.main = function (m_project_id, m_map) {
        project_id = m_project_id;
        map = m_map;

        // step through the methods named by workflow
        main_callback();


        //
        // event listeners
        //

        // listen to or pause the stream
        $('.jp-play').on('click', listen);

        // update the stream
        $("#update-stream").click(function () {
            show_spinner('Updating the stream...', 2);
            modify_stream();
        });

        // change tag selections
        $('#voicemap-nav').on('click', 'input.tag', filter_click);

        // show project config details
        $('#project-config-toggle').on('click', function () {
            $('#project-config').toggle();
        });
    };


    /**
     * show/hide elements on the map based on what tags are checked
     */
    function filter_click(event) {
        var tag_label = $(this).parent('label');
        if (tag_label.find('input:checked').length) {
            tag_label.css({backgroundColor: '#719EE3'});
        }
        else {
            tag_label.css({backgroundColor: '#aaaaaa'});
        }

        var tag_id = $(this).context.id.split(/\-/)[1];
        if ($('#tag_boolean_and').prop('checked')) {
            filter_and();
        }
        else {
            filter_or(tag_id, $(this).context.checked);
        }

        if (is_listening) {
            modify_stream();
        }
    }


    /**
     * filter visible assets, showing only those that match all checked tags.
     */
    function filter_and() {
        $.each(all_assets, function (i, item) {
            var is_visible = true;

            $.each($('input.tag:checked'), function (j, tag) {
                var tag_id = tag.id.split(/\-/)[1];
                if (!item.has_tag(tag_id)) {
                    is_visible = false;
                    return;
                }
            });
            item.setVisible(is_visible);
            item.circle.setVisible(is_visible);
        });

    }


    /**
     * filter visible assets, showing only those that match one or more checked tags.
     */
    function filter_or(tag_id, is_on) {
        $.each(all_assets, function (i, item) {
            if (item.has_tag(tag_id)) {
                item.setVisible(is_on);
                item.circle.setVisible(is_on);
            }
        });
    }


    /**
     * pluck the first item off the workflow list and call it. this method is assigned
     * as a callback for each of the workflow functions, so this steps through the
     * workflow in a synchronous manner, making sure each step is complete before
     * calling the next one.
     */
    function main_callback() {
        var loading = $('#voicemap-loading');
        loading.show();
        if (workflow.length) {
            var fx = workflow.shift();
            fx();
        }
        else {
            loading.hide();
        }
    }


    /**
     * call RW's get_config for the project. get_config's datastructure is an array rather
     * than a hash, even though the values are named hashes. this means we have to loop
     * through the array to collect the names of the hashes in order to have convenient
     * properties like config.project.project_id.
     *
     * The following values are pulled from the config call: device, session, project,
     * server, speakers, audiotracks. Anything else returned will be ignored.
     *
     */
    function get_config() {
        function parse_config(data) {
            var fields = {'device': '', 'session': '', 'project': '', 'server': '', 'speakers': '', 'audiotracks': ''};
            $.each(data, function (i, item) {
                $.each(fields, function (key, val) {
                    if (item[key]) {
                        config[key] = item[key];
                        return false;
                    }
                });
            });

            // push project config into HTML-friendly list
            $('#project-config').html(build_config(config));

            main_callback();
        }

        $.ajax({
            url: options.url,
            data: {operation: 'get_config', project_id: project_id},
            dataType: 'json',
            success: parse_config,
            error: function (req, e_text, err) {
                console.error('could not retrieve config: ' + e_text + err);
            }
        });
    }


    /**
     * convert project config into an HTML string, serializing objects
     * (i.e. device, session, project, server) but ignoring arrays
     * (i.e. speakers, audiotracks).
     */
    function build_config(list) {
        var s = '<dl>';
        $.each(list, function (key, value) {
            s += '<dt>' + key + '</dt><dd>';

            // arrays values: ignore
            if (Array.isArray(value)) {
            }
            // object values: serialize recursively for display
            else if ((typeof value == "object") && (value !== null)) {
                s += build_config(value);
            }
            // scalar values: display
            else {
                s += value;
            }

            s += '</dd>'

        });

        s += '</dl>';

        return s;
    }


    /**
     * call RW's get_tags for the project
     */
    function get_tags() {
        $.ajax({
            url: options.url,
            data: {operation: "get_tags", project_id: project_id},
            dataType: 'json',
            success: function (data) {
                tags = data.listen;
                tags.sort(tag_sort);
                main_callback();
            },
            error: function (data) {
                console.error('could not retrieve tags');
            }
        });
    }


    /**
     * call RW's get_available_assets for the project
     */
    function get_assets() {
        $.ajax({
            url: options.url,
            data: {operation: "get_available_assets", project_id: project_id},
            dataType: 'json',
            success: function (data) {
                assets = data.assets;
                main_callback();
            },
            error: function (data) {
                console.error('could not retrieve tags');
            }
        });
    }


    /**
     * return an HTML string to be used as a marker's info window
     */
    function create_info_window(id, descp, fn, fnwav, id) {
        var marker_div = '<div class="markerDiv">' + descp + '<br /><audio controls="controls"><source src="' + fn + '" type="audio/mpeg" /><source src="' + fnwav + '" type="audio/wav" /><object type="application/x-shockwave-flash" data="js/player.swf" id="audioplayer' + id + '" height="24" width="290"><param name="movie" value="js/player.swf"><param name="FlashVars" value="playerID=' + id + '&amp;soundFile=' + fn + '&titles=' + descp + '"><param name="quality" value="high"><param name="menu" value="false"><param name="wmode" value="transparent"></object></audio><div>' + id + '</div></div>';

        var iw = new google.maps.InfoWindow({
            content: marker_div
        });

        return iw;
    }


    /**
     * instantiate a new google.maps.Marker and return it
     */
    function create_marker(item, iw, color) {
        var marker_img = new google.maps.MarkerImage('http://www.google.com/intl/en_us/mapfiles/ms/micons/' + color + '-dot.png');
        var point = new google.maps.LatLng(item.latitude, item.longitude);

        var marker = new google.maps.Marker({
            position: point,
            map: map,
            icon: marker_img
        });

        marker.infoWindow = iw;
        marker.rw_tags = [];
        if (item.tags) {
            marker.rw_tags = item.tags;
        }
        marker.has_tag = function (tag_id) {
            var has_tag = false;
            $.each(this.rw_tags, function (i, tag) {
                if (tag.tag_id == tag_id) {
                    has_tag = true;
                    return;
                }
            });
            return has_tag;
        }

        // on click, close all other markers' windows and then open this one
        google.maps.event.addListener(marker, 'click', function () {
            for (var i = 0; i < all_assets.length; i++) {
                all_assets[i].infoWindow.close();
            }
            marker.infoWindow.open(map, marker);
        });


        return marker;
    }


    /**
     * add assets to the map
     */
    function map_assets() {
        $.each(assets, function (i, item) {

            if (!item.submitted || item.mediatype != 'audio') {
                return;
            }

            // get a list of this item's tags, keyed by tag_id
            var item_tags = [];
            $.each(item.tags, function (j, tag) {
                item_tags[tag.tag_id] = tag;
            });

            // loop through all tags, which are sorted by
            var desc = [];
            $.each(tags, function (i, item) {
                $.each(item.options, function (j, option) {
                    if (item_tags[option.tag_id]) {
                        /*desc.push(item.name + ': ' + item_tags[option.tag_id].localized_value); */
                        desc.push('<div class=\"ib_' + item_tags[option.tag_id].tag_category_name + '\">' + item_tags[option.tag_id].localized_value + '</div>');
                    }

                });
            });

            var fnmp3 = item.asset_url.replace("wav", "mp3");
            var id = item.asset_id;
            var iw = create_info_window(item.asset_id, desc.join(' '), fnmp3, item.asset_url, id);
            var marker = create_marker(item, iw, 'blue');
            var radius = config.project.recording_radius || 5;
            all_assets.push(marker);


            var circle = {
                strokeColor: '#6292CF',
                strokeOpacity: 0.8,
                strokeWeight: 1,
                fillColor: '#6292CF',
                fillOpacity: 0.25,
                map: map,
                center: new google.maps.LatLng(item.latitude, item.longitude),
                radius: radius
            };
            marker.circle = new google.maps.Circle(circle);

        });

        main_callback();
    }


    /**
     * add active speakers to the map, including attenuation border
     */
    function map_speakers() {


        $.each(config.speakers, function (i, item) {
            if (item.activeyn == true) {
                map.data.addGeoJson({
                    "type": "Feature",
                    "geometry": item.shape,
                    "properties": {
                        "speaker_id": item.id,
                        "name": "outer"
                    }
                });
                map.data.addGeoJson({
                    "type": "Feature",
                    "geometry": item.attenuation_border,
                    "properties": {
                        "speaker_id": item.id,
                        "name": "inner"
                    }
                });
                // map.data.setStyle({
                //     fillColor: 'green',
                //     strokeWeight: 1
                // });
                map.data.setStyle(function(feature) {
                    if (feature.getProperty('name') == "outer") {
                        return {
                            fillColor: '#aaaaaa',
                            fillOpacity: .5,
                            strokeWeight: 1,
                            strokeOpacity: .5
                        };
                    }
                    else if (feature.getProperty('name') == "inner") {
                        return {
                            fillColor: '#555555',
                            fillOpacity: 0,
                            strokeWeight: 1,
                            strokeOpacity: .2
                        };
                    }
                });
            }
        });

        main_callback();
    }


    /**
     * Add draggable listening pin that can be dragged to a new location to hear the
     * audio as streamed from that location.
     */
    function add_listening_pin() {
        var marker_img = new google.maps.MarkerImage('http://www.google.com/intl/en_us/mapfiles/ms/micons/green-dot.png');
        var mapCenter = new google.maps.LatLng(config.project.latitude, config.project.longitude);
        listening_pin = new google.maps.Marker({
            position: mapCenter,
            map: map,
            icon: marker_img,
            draggable: true
        });
        map.setCenter(mapCenter);

        google.maps.event.addListener(listening_pin, "dragend", function (event) {
            modify_stream();
        });

        main_callback();
    }


    /**
     * Construct and return a URL to use for a request_stream or modify_stream request.
     * @param string operation: name of the operation to add to the URL, i.e. request_stream or modify_stream
     * @return string a URL
     */
    function get_url(operation, lat, lng) {
        var l = $('input.tag:checked').map(function () {
            return this.value;
        }).get().join(',');

        var url = options.url + '?operation=' + operation + '&session_id=' + config.session.session_id + '&tags=' + l;

        var listener_location = listening_pin.getPosition();
        url += '&latitude=' + listener_location.lat() + '&longitude=' + listener_location.lng();

        console.log('url will be ' + url);

        return url;
    }

    /**
     * Build the data for a GET request
     */
    function get_query(operation) {
        var listener_location = listening_pin.getPosition();
        var l = $('input.tag:checked').map(function () {
            return this.value;
        }).get().join(',');

        return {
            tags: l,
            operation: operation,
            session_id: config.session.session_id,
            latitude: listener_location.lat(),
            longitude: listener_location.lng()
        };
    }

    /**
     * Request an audio stream to listen to
     */
    function listen() {
        // don't generate a new stream if an existing stream was paused
        if (is_listening) {
            console.log('already listening!');
            return;
        }

        if ($(".tag").size() < 2) {
            alert("Please select at least one option from each question/column and try again.\n\nThanks!");
            return;
        }

        show_spinner('Generating audio stream...', 1);

        if (!iOSdevice) {
            $("#jquery_jplayer_1").jPlayer("destroy");
        } else {
            $('#audio-container input').remove();
        }

        $.ajax({
            url: options.url,
            data: get_query('request_stream'),
            dataType: 'json',
            success: function (data) {

                if (!iOSdevice) {
                    var stream = {mp3: data.stream_url};
                    var ready = false;

                    $("#jquery_jplayer_1").jPlayer({
                        ready: function (event) {
                            console.log('EVENT: READY');
                            ready = true;
                            $(this).jPlayer("setMedia", stream);
                            $(this).jPlayer("play");
                        },
                        pause: function () {
                            console.log('EVENT: PAUSE');
                            $(this).jPlayer("clearMedia");
                        },
                        error: function (event) {
                            console.log('EVENT: ERROR');
                            if (ready && event.jPlayer.error.type === $.jPlayer.error.URL_NOT_SET) {
                                // Setup the media stream again and play it.
                                $(this).jPlayer("setMedia", stream).jPlayer("play");
                            }
                        },
                        swfPath: "../js",
                        supplied: "mp3",
                        preload: "none"
                    });
                } else {
                    $('#audio-container').append('<div><audio autoplay="autoplay" controls="controls"><source src="' + data.stream_url + '" type="audio/mpeg" />Your browser does not support the audio element.</audio></div>');
                }

                is_listening = true;

                modify_stream();
                $('#update-stream').show();
            },
            error: function (data) {
                console.log('stream listen failure');
            }
        });

    }

    /**
     * sort tags by order
     */
    function tag_sort(a, b) {
        return a.order > b.order ? 1 : a.order < b.order ? -1 : 0;
    }


    /**
     * do some browser sniffing to determine the best listen button to show.
     * Firefox is still DOA; iOS devices use native HTML5 controls, and everything else
     * gets a JPlayer widget.
     */
    function show_listening_button() {
        iOSdevice = ( navigator.userAgent.match(/(iPad|iPhone|iPod)/i) ? true : false );
        //detect Firefox to warn of streaming issue
        var is_firefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
        //var is_mac = navigator.appVersion.indexOf("Mac") > -1;
        if (is_firefox) {
            alert("Unfortunately, Firefox is unable to stream mp3 audio.  Please use a different browser such as Chrome or Safari to listen.\n\nSorry for the inconvenience and thanks!");
        }

        if (iOSdevice) {
            $('.full-float-block').first().remove();
            $('#content').prepend('<div class="full-float-block" id="audio-container"><input type="button" class="jp-play" value="Listen" /><center><div id="spinner-1" class="spinner"><img src="/images/ajax-loader.gif"/><span><em>Updating the stream...</em><span></div></center></div>');

        }
        else {
            $("#jquery_jplayer_1").jPlayer({
                ready: function () {
                    $(this).jPlayer("setMedia", {
                        mp3: "http://localhost:8000/stream4567.mp3"
                    });
                },
                //swfPath: "http://halseyburgund.com/dev/deeptime/rw",
                supplied: "mp3",
                preload: "auto"
            });
        }

        // show the controls, since they are hidden by default while they are unconfigured
        $('#listen-controls').show();

        // listen to a stream
        $('.jp-play').on('click', function () {
            console.log('clicked listen');
        });


        main_callback();
    }


    /**
     * list tags that may be used to filter the map points/update the stream.
     */
    function show_filters() {
        var parsed_tags = parse_tags(tags);
        $('#voicemap-nav').append(parse_tags(tags)).show();

        var checkboxLabels = $("input[type='checkbox']").parent('label');
        checkboxLabels.css({backgroundColor: '#719EE3'});

        main_callback();
    }


    /**
     * Given a list of tags as from a get_tags request, transform the list into an HTML
     * string and return it.
     */
    function parse_tags(data) {
        var str = '';
        $.each(data, function (i, item) {
            if (item.select == 'single') {
                str += '<ul class="filtering-options"><li class="question">' + item.name + '</li>';
                str += show_single(item);
                str += '</ul>';
            }
            else if (item.select == 'multi') {
                str += '<ul class="filtering-options"><li class="question">' + item.name + '</li>';
                str += show_multi(item);
                str += '</ul>';
            }
            else if (item.select == 'multi_at_least_one') {
                str += '<ul class="filtering-options"><li class="question">' + item.name + '</li>';
                str += show_multi(item);
                str += '</ul>';
            }
            else if (item.select == 'one_or_all') {
//                show_one_or_all(item);
            }
        });

        return str;
    }


    /**
     * Given a JSON object representing a select-one item, convert it to an HTML select item
     * and return it.
     *
     * @param field
     * @returns {String}
     */
    function show_single(field) {
        var str = '';
        var newString = "";
        $.each(field.options, function (i, item) {
            var selected = '';
            $.each(field.defaults, function (j, field_default) {
                if (field_default == item.tag_id) {
                    selected = 'selected';
                }

            });
            var splitString = item.value.split('|');
            if (splitString.length > 1) {
                newString = splitString[0] + ", " + splitString[1];
            } else {
                newString = splitString[0];
            }

            str += '<li><label for="tag-' + item.tag_id + '"><input type="radio" class="tag" name="' + field.code + '" id="tag-' + item.tag_id + '" value="' + item.tag_id + '">' + newString + '</label></li>';

        });

        return str;

    }


    /**
     * Given a JSON object representing a select-multi item, convert it to a string of
     * HTML checkboxes and return it.
     *
     * @param field
     * @returns {String}
     */
    function show_multi(field) {
        var str = '';

        $.each(field.options, function (i, item) {
            var checked = '';

            $.each(field.defaults, function (j, field_default) {

                if (field_default == item.tag_id) {
                    checked = 'checked';
                }

            });

            var splitString = item.value.split('|');
            var newString = "";
            if (splitString.length > 1) {
                newString = splitString[0] + ", " + splitString[1];
            } else {
                newString = splitString[0];
            }

            str += '<li><label class="tag" for="tag-' + item.tag_id + '"><input type="checkbox" name="' + item.tag_id + '[]" id="tag-' + item.tag_id + '" value="' + item.tag_id + '" ' + checked + ' class="tag">' + newString + '</label></li>';
        });

        return str;

    }


    function show_spinner(text, index) {
        if (!index) {
            index = 1;
        }
        var numLow = 3;
        var numHigh = 6;

        var adjustedHigh = (parseFloat(numHigh) - parseFloat(numLow)) + 1;

        var numRand = Math.floor(Math.random() * adjustedHigh) + parseFloat(numLow);
        var whichSpinner = '#spinner-' + index;
        $(whichSpinner + ' span').html('<em>' + text + '</em>');
        $(whichSpinner).css({visibility: 'visible'});
        $(whichSpinner).fadeIn(300).delay(numRand * 1000).fadeOut(300);
    }


    /**
     * update the existing audio stream
     */
    function modify_stream() {
        if (!is_listening) {
            listen();
            return;
        }
        $.ajax({
            url: options.url,
            data: get_query('move_listener'),
            dataType: 'json',
            success: function (data) {
                console.log('stream modified');
            },
            error: function (data) {
                console.log('stream modify failure');
            }
        });
    }


    return this;

};

