// get around some jQuery namespace conflicts in js files... 
var $ = django.jQuery;
var jQuery = django.jQuery;


function update_MasterUI_edit_form() {
    // update the edit form fields with data for the selected masterui 
    $form=$('#setup_tag_ui_form');
    var datastring = $form.serialize();
    console.log('datastring:'+ datastring);
    $.ajax({
        type: "POST",
        url: $form.attr('action'),
        dataType: 'html',
        data: datastring,
        success: function(result)
        {
            /* The div contains now the updated form */
            $('#mui_edit_form_wrapper').html(result);
            rewriteSortedMultiCheckbox();
        }
    });

    //don't submit the form
    return false;
}

