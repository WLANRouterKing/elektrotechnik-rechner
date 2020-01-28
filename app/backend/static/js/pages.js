$(document).ready(function () {

    var page_elements_dialog = $("#page-element-overview-dialog").dialog({
        buttons: [
            {
                text: "schließen",
                click: function () {
                    $(this).dialog("close");
                }
            }
        ]
    });

    page_elements_dialog.dialog("close");

    $('.button-add-page-element').bind("click touch", function () {
        page_elements_dialog.dialog("open");
    });

    $('.button-display-tab-content').bind("click touch", function () {
        $(this).toggleClass('clicked');

        if ($(this).hasClass('clicked')) {
            $(this).parent('.tab').children('.form-group').addClass('hidden');
            $(this).html('<span class="oi oi-arrow-thick-bottom"></span>Inhalt einblenden');
        } else {
            $(this).parent('.tab').children('.form-group').removeClass('hidden');
            $(this).html('<span class="oi oi-arrow-thick-top"></span>Inhalt ausblenden');
        }

    });

    $('.page-element-item').bind("click touch", function () {
        $('#page-elements').append('<div class="page-element-content-item">' + $(this).attr('eid') + '</div>');
    });

});