$(document).ready(function(){

    var default_lng = "-71.057205";
    var default_lat = "42.355709";
    var mapOptions = {
        zoom: 10,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        center: new google.maps.LatLng(default_lat,default_lng)
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
        draggable: true
    });

    google.maps.event.addListener(marker, 'dragend', function(mouseEvent) {
        savePosition(mouseEvent.latLng);
    });

    google.maps.event.addListener(map, 'click', function(mouseEvent){
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
                savePosition(location);
            }
        });
    });
});
//}(django.jQuery));