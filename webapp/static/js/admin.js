function show_lvl_1(value=true) {
    if (value) {
        $('.lvl-2').hide();
        $('.lvl-1').show();
        $('.add-btn').show();
    } else {
        $('.lvl-1').hide();
        $('.lvl-2').show();
        $('.add-btn').hide();
    }
};

var toast_num = 1;
var new_toast = '<div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-delay="4000" id="toast-id"> \
                        <div class="toast-header bg-primary text-white">toast-title \
                            <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close"> \
                                <span aria-hidden="true">&times;</span> \
                            </button> \
                        </div> \
                    </div>'

function show_message(text) {
    console.log(text);
    var new_id = 'toast' + toast_num;
    $('.my-toast').append(new_toast.replace('toast-title', text).replace('toast-id', new_id));
    $('#'+new_id).toast('show');
    toast_num += 1;
};