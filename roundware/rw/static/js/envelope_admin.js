
var next_tags_inserted_gets_copied_vals = false;
var asset_set_selector = "div.dynamic-asset_set";

function copyAssetAttrs(obj) {   
    // copy the form values of the previous Asset to the new subform,
    // excluding the file input.
    var older_sib = $(obj).prev();

    //copy tags separately, otherwise the number of DOM elements in the older
    //sibling is different and throws off our $.each loop
    var form_el_selector = "fieldset div.form-row:not(div[class~='file']) input:not([id*='searchbox']):not([id*='tags']), fieldset div.form-row:not(div[class~='file']) select:not([id*='tags']), fieldset div.form-row:not(div[class~='file']) textarea";

    if ($(older_sib).is(asset_set_selector)) {
        var older_sib_formels = $(older_sib).find(form_el_selector);
        $.each($(obj).find(form_el_selector), function(key, el) {
            el.value = older_sib_formels[key].value;
        });
    }

}

function copyTagsValuesFromOlderSibling(obj) {
    var tags_on_selector = "select[id*='tags_to']";
    var asset_set = $(obj).closest(asset_set_selector);
    var prev_asset_set = $(asset_set).prevAll(asset_set_selector).first();
    var this_tags_on_el = $(obj).find(tags_on_selector);
    var older_tags_on_el = $(prev_asset_set).find(tags_on_selector);
    var older_options = $(older_tags_on_el).find('option');
    $(older_options).each( function() {
        //console.log("copying option:"+this+" into "+obj.id);
        $(obj).append($("<option/>", {
                'value': this.value, 'text': this.text}));
    });


    // $.each($(this_tags_on_el).find('option'), function(key, el) {
    //     el.value = older_options[key].value;
    // })
}

function buildAssetAccordion() {
    var outer = $('#asset_set-group');
    // first need to wrap Asset fieldsets in an extra div
    $(outer).find(asset_set_selector).each(
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
    var num_panels = $(outer).find(asset_set_selector).length

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
    if ($(element).is(asset_set_selector)) {

        // when the tags_to select is inserted into DOM, then copy the tags from
        // the older sibling.
        next_tags_inserted_gets_copied_vals = true;
        //console.log('copy asset form values now for: '+ e.target.id);
        copyAssetAttrs(e.target);
        hideMediaDisplay();
        setLocationMaps();
        $(e.relatedNode).accordion("destroy");
        buildAssetAccordion();
        num_panels = $(e.relatedNode).find(asset_set_selector).length;
        $(e.relatedNode).accordion("option","active",num_panels-1);

    }
    // handle copying of select tags to new Asset
    else if ($(element).is("select[id*='tags_to']")) {
        if (next_tags_inserted_gets_copied_vals) {
            console.log('copy tags now for: '+ e.target.id);
            copyTagsValuesFromOlderSibling(e.target);
            next_tags_inserted_gets_copied_vals = false;
        }
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

