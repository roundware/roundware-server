$(function() {

    $('#side-menu').metisMenu();

    $('#side-menu.nav li').on( "click", function( event ) {
        console.log("nav element clicked)");
        // return false;
    } );

    $('#nav-dashboard').on( "click", function( event ) {
        $('#nav-charts').removeClass("active");
        $('#nav-charts li').removeClass("active");
    } );
    $('#nav-charts').on( "click", function( event ) {
        $('#nav-dashboard').removeClass("active");
    } );

});

//Loads the correct sidebar on window load,
//collapses the sidebar on window resize.
$(function() {
    $(window).bind("load resize", function() {
        console.log($(this).width())
        if ($(this).width() < 768) {
            $('div.sidebar-collapse').addClass('collapse')
        } else {
            $('div.sidebar-collapse').removeClass('collapse')
        }
    })
})
