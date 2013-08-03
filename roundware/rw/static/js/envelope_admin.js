
function copyAssetAttrs(obj) {
    // copy the form values of the previous Asset to the new subform,
    // excluding the file input.
    var oldersib = $(obj).prev();
    var formelselector = "fieldset div.form-row:not(div[class~='file']) input, fieldset div.form-row:not(div[class~='file']) select, fieldset div.form-row:not(div[class~='file']) textarea";

    if ($(oldersib).is("div.dynamic-asset_set")) { 
        var oldersib_formels = $(oldersib).find(formelselector);
        $.each($(obj).find(formelselector), function(key, el) {
            el.value = oldersib_formels[key].value;
        });
    }
}

function buildAssetAccordion() {
    var outer = $('#asset_set-group');
    // first need to wrap Asset fieldsets in an extra div
    $(outer).find('div.dynamic-asset_set').each(
        function(){
            if ($(this).find('div.accordionwrapper').length==0) {
                $(this).find('fieldset').wrapAll("<div class='accordionwrapper'/>");   
            }
            // have to move the delete checkbox since accordion header eats
            // all of the click events
            $(this).find('span.delete').prependTo($(this).find('.accordionwrapper'));

        }
    );

    // check for error notices
    var error_divs = $(outer).find('div.errors');
    var num_panels = $(outer).find('div.dynamic-asset_set').length

    $(outer).accordion({
        header: '.dynamic-asset_set h3', 
        collapsible: false, 
        active: ($(error_divs).length) ? num_panels-1 : false,
        change: function(e, ui) {
            // force a redraw of the map after it has gone offscreen
            // as inactive accordion pane.
            map = maps[ui.options.active];
            google.maps.event.trigger(map, 'resize');
            map.setZoom(map.getZoom()); 
            map.setCenter(map.marker.getPosition());

        }});
}

$(document).bind("DOMNodeInserted", function(e) {
    //console.log(e);
    var element = e.target;
    if ($(element).is('div.dynamic-asset_set')) {
        copyAssetAttrs(e.target);
        hideMediaDisplay();
        setLocationMaps();
        $(e.relatedNode).accordion("destroy");
        buildAssetAccordion();
        num_panels = $(e.relatedNode).find('div.dynamic-asset_set').length;
        $(e.relatedNode).accordion("option","active",num_panels-1);

    }
});


$(document).ready(function() {
    // move initial select assets field below inlines
    var select_assets = $("div.form-row.assets");
    $(select_assets).insertAfter($('#asset_set-group'));
    // make it an accordion with a new header
    $(select_assets).wrapAll("<div id='select_assets_wrapper' class='inline-group'/>");
    $(select_assets).before('<h2>Select assets from list</h2>');
    $('div#select_assets_wrapper').accordion({
        header: 'h2', 
        collapsible: true, 
        active: false,   
    });


    // set up accordion on Assets
    buildAssetAccordion();
});

