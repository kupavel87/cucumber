function show_lvl_1(value = true) {
    if (value) {
        $('.lvl-2').hide();
        $('.lvl-1').show();
    } else {
        $('.lvl-1').hide();
        $('.lvl-2').show();
    }
};

var toast_num = 1;
var new_toast = '<div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-delay="6000" id="toast-id"> \
                        <div class="toast-header bg-success text-white">toast-title \
                            <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close"> \
                                <span aria-hidden="true">&times;</span> \
                            </button> \
                        </div> \
                    </div>'

function show_message(text) {
    console.log(text);
    var new_id = 'toast' + toast_num;
    $('.my-toast').append(new_toast.replace('toast-title', text).replace('toast-id', new_id));
    $('#' + new_id).toast('show');
    toast_num += 1;
};


function reload_area() {
    if ($('.chapter-nav select').val() != "0") {
        $('.chapter-nav option:selected').change();
    } else {
        $('.chapter-nav .active').click();
    };
};

function Edit_Item(button) {
    console.log('edit_item');
    $(".modal-content").html('');
    $.get(button.attr('link'), function (data) {
        $(".modal-content").html(data.html);
        $('#CreateModal').modal('show');
    });
};

function Del_Item(button) {
    console.log('del_item');
    $.get(button.attr('link'), function (data) {
        console.log(data.status);
        show_message(data.text);
        reload_area();
    });
};

function Edit_Done(form) {
    event.preventDefault();
    console.log('edit_done');
    $.post(form.attr('action'), form.serialize(), function (data) {
        console.log(data.status);
        $('#CreateModal').modal('hide');
        show_message(data.text);
        reload_area();
    });
};

function Enter_Item(button) {
    $.get(button.attr('link'), function (data) {
        $('.lvl-2-content').html(data.html);
        show_lvl_1(false);
    });
};