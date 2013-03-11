/**
 * A distance widget that will display a circle that can be resized and will
 * provide the radius in km.
 *
 * @param {google.maps.Map} map The map on which to attach the distance widget.
 * @param {google.maps.Marker} marker The marker to which to attach the radius widget.
 * @param {int} radius The radius of the circle.
 * @param {String} color The strokeColor of the circle.
 *
 * @constructor
 */
function DistanceWidget(map, marker, radius, color) {
    this.set('map', map);
    this.set('position', marker.getPosition());

    // Bind the marker map property to the DistanceWidget map property
    marker.bindTo('map', this);

    // Bind the marker position property to the DistanceWidget position
    // property
    marker.bindTo('position', this);

    // Create a new radius widget
    var radiusWidget = new RadiusWidget(radius, color);

    // Bind the radiusWidget map to the DistanceWidget map
    radiusWidget.bindTo('map', this);
    radiusWidget.bindTo('center', this, 'position');

    // Bind to the radiusWidgets' distance property
    this.bindTo('distance', radiusWidget);

    // Bind to the radiusWidgets' bounds property
    this.bindTo('bounds', radiusWidget);
}


DistanceWidget.prototype = new google.maps.MVCObject();


/**
 * A radius widget that add a circle to a map and centers on a marker.
 *
 * @param {int} radius The radius of the circle to create, in meters.
 * @param {String} color The strokeColor of the circle.
 *
 * @constructor
 */
function RadiusWidget(radius, color) {
    var circle = new google.maps.Circle({
        strokeWeight: 2,
        strokeColor: color,
        fillOpacity: 0
    });

    // Set the distance property value, default to 50km.
    this.set('distance', radius);

    // Bind the RadiusWidget bounds property to the circle bounds property.
    this.bindTo('bounds', circle);

    // Bind the circle center to the RadiusWidget center property
    circle.bindTo('center', this);

    // Bind the circle map to the RadiusWidget map
    circle.bindTo('map', this);

    // Bind the circle radius property to the RadiusWidget radius property
    circle.bindTo('radius', this);

    this.addSizer_();
}
RadiusWidget.prototype = new google.maps.MVCObject();


/**
 * Update the radius when the distance has changed.
 */
RadiusWidget.prototype.distance_changed = function() {
    this.set('radius', this.get('distance') * 1);
};


/**
 * Add the sizer marker to the map.
 *
 * @private
 */
RadiusWidget.prototype.addSizer_ = function() {
    var sizer = new google.maps.Marker({
        draggable: true,
        title: 'Drag me!',
        raiseOnDrag: false,
        icon: '/static/imgs/resize-off.png'
    });

    sizer.bindTo('map', this);
    sizer.bindTo('position', this, 'sizer_position');

    var me = this;
    google.maps.event.addListener(sizer, 'drag', function() {
        // Set the circle distance (radius)
        me.setDistance();
    });
};


/**
 * Update the center of the circle and position the sizer back on the line.
 *
 * Position is bound to the DistanceWidget so this is expected to change when
 * the position of the distance widget is changed.
 */
RadiusWidget.prototype.center_changed = function() {
    var bounds = this.get('bounds');

    // Bounds might not always be set so check that it exists first.
    if (bounds) {
        var lng = bounds.getNorthEast().lng();
        var lat = bounds.getNorthEast().lat();

        // Put the sizer at center, right on the circle.
        var position = new google.maps.LatLng(this.get('center').lat(), lng);
        this.set('sizer_position', position);
    }
};


/**
 * Calculates the distance between two latlng locations in km.
 * @see http://www.movable-type.co.uk/scripts/latlong.html
 *
 * @param {google.maps.LatLng} p1 The first lat lng point.
 * @param {google.maps.LatLng} p2 The second lat lng point.
 * @return {int} The distance between the two points in km.
 * @private
 */
RadiusWidget.prototype.distanceBetweenPoints_ = function(p1, p2) {
    if (!p1 || !p2) {
        return 0;
    }

    var R = 6371; // Radius of the Earth in km
    var dLat = (p2.lat() - p1.lat()) * Math.PI / 180;
    var dLon = (p2.lng() - p1.lng()) * Math.PI / 180;
    var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(p1.lat() * Math.PI / 180) * Math.cos(p2.lat() * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    var d = R * c;
    return d;
};


/**
 * Set the distance of the circle based on the position of the sizer.
 */
RadiusWidget.prototype.setDistance = function() {
    // As the sizer is being dragged, its position changes.  Because the
    // RadiusWidget's sizer_position is bound to the sizer's position, it will
    // change as well.
    var pos = this.get('sizer_position');
    var center = this.get('center');
    var distance = this.distanceBetweenPoints_(center, pos) * 1000;

    // Set the distance property for any objects that are bound to it
    this.set('distance', distance);
};


$(document).ready(function(){
    var default_lng = document.getElementById("id_longitude").value;
    var default_lat = document.getElementById("id_latitude").value;
    var default_lng_missing, default_lat_missing = false;
    if ( default_lng == "" ) {
        default_lng_missing = true;
        default_lng = "-71.057205";
    }
    if ( default_lat == "" ) {
        default_lat_missing = true;
        default_lat = "42.355709";
    }
    var mapOptions = {
        zoom: 10,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        center: new google.maps.LatLng(default_lat, default_lng)
    };

    var map = new google.maps.Map(document.getElementById("map"),mapOptions);

    function savePosition(point)
    {
        var input = document.getElementById("map");
        input.value = point.lat().toFixed(6) + "," + point.lng().toFixed(6);
        document.getElementById("id_latitude").value = point.lat().toFixed(6);
        document.getElementById("id_longitude").value = point.lng().toFixed(6);

        map.panTo(point);
    }

    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(default_lat,default_lng),
        map: map,
        draggable: true,
        visible: false
    });


    //Create the distance widget
    var minDistanceField = document.getElementById("id_mindistance");
    var maxDistanceField = document.getElementById("id_maxdistance");
    if ( maxDistanceField && minDistanceField ) {
        var mindistance = minDistanceField.value;
        var maxdistance = maxDistanceField.value;
        var minDistanceWidget = new DistanceWidget(map, marker, mindistance, "#ff0000");
        var maxDistanceWidget = new DistanceWidget(map, marker, maxdistance, "#0000ff");

        google.maps.event.addListener(minDistanceWidget, 'distance_changed', function() {
            minDistanceField.value = Math.round(minDistanceWidget.get('distance'));
        });

        google.maps.event.addListener(minDistanceWidget, 'position_changed', function() {
            return true;
        });

        google.maps.event.addListener(maxDistanceWidget, 'distance_changed', function() {
            maxDistanceField.value = Math.round(maxDistanceWidget.get('distance'));
        });

        google.maps.event.addListener(maxDistanceWidget, 'position_changed', function() {
            minDistanceWidget.set('position', maxDistanceWidget.get('position'));
        });

    }

//    $("#id_mindistance").change(function() {
//        console.log(this.value);
//        minDistanceWidget.set('distance', this.value);
//    });
//
//    $("#id_maxdistance").change(function() {
//        console.log(this.value);
//        maxDistanceWidget.set('distance', this.value);
//    });

    if (default_lat_missing == false || default_lng_missing == false) {
        marker.setVisible(true);
    }

    google.maps.event.addListener(marker, 'dragend', function(mouseEvent) {
        savePosition(mouseEvent.latLng);
    });

    google.maps.event.addListener(map, 'click', function(mouseEvent){
        if (!marker.getVisible()) {
            marker.setVisible(true);
        }
        marker.setPosition(mouseEvent.latLng);
        savePosition(mouseEvent.latLng);
    });

    var geocoder = new google.maps.Geocoder();

    $(function() {
        $("#searchbox").autocomplete({

            source: function(request, response) {

                if (geocoder == null){
                    geocoder = new google.maps.Geocoder();
                }
                geocoder.geocode( {'address': request.term }, function(results, status) {
                    if (status == google.maps.GeocoderStatus.OK) {

                        var searchLoc = results[0].geometry.location;
                        var lat = results[0].geometry.location.lat();
                        var lng = results[0].geometry.location.lng();
                        var latlng = new google.maps.LatLng(lat, lng);
                        var bounds = results[0].geometry.bounds;

                        geocoder.geocode({'latLng': latlng}, function(results1, status1) {
                            if (status1 == google.maps.GeocoderStatus.OK) {
                                if (results1[1]) {
                                    response($.map(results1, function(loc) {
                                        return {
                                            label: loc.formatted_address,
                                            value: loc.formatted_address,
                                            bounds: loc.geometry.bounds,
                                            latitude: loc.geometry.location.lat(),
                                            longitude: loc.geometry.location.lng()
                                        }
                                    }));
                                }
                            }
                        });
                    }
                });
            },
            select: function(event,ui){
                var pos = ui.item.position;
                var lct = ui.item.locType;
                var bounds = ui.item.bounds;

                if (bounds) {
                    map.fitBounds(bounds);
                }
                var location = new google.maps.LatLng(ui.item.latitude, ui.item.longitude);
                marker.setPosition(location);
                if (!marker.getVisible()) {
                    marker.setVisible(true);
                }
                map.setZoom(15);
                savePosition(location);
            }
        });
    });
});
//}(django.jQuery));
