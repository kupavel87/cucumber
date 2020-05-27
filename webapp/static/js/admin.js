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