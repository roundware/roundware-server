
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

    $(outer).accordion({header: '.dynamic-asset_set h3', collapsible: true, active: false});
}

$(document).bind("DOMNodeInserted", function(e) {
    //console.log(e);
    var element = e.target;
    if ($(element).is('div.dynamic-asset_set')) {
        copyAssetAttrs(e.target);
        setLocationMaps();
        $(e.relatedNode).accordion("destroy");
        buildAssetAccordion();
        num_panels = $(e.relatedNode).find('div.dynamic-asset_set').length;
        $(e.relatedNode).accordion("option","active",num_panels-1);

    }
});

$(document).ready(function() {
    // set up accordion on Assets
    buildAssetAccordion();
});

