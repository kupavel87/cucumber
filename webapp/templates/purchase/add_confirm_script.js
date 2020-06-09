var icon_expand = '<svg class="bi bi-caret-down-fill" width="1.5em" height="1.5em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"> \
                        <path d="M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z" /> \
                    </svg>';
var icon_collapse = '<svg class="bi bi-caret-up-fill" width="1.5em" height="1.5em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"> \
                        <path d="M7.247 4.86l-4.796 5.481c-.566.647-.106 1.659.753 1.659h9.592a1 1 0 0 0 .753-1.659l-4.796-5.48a1 1 0 0 0-1.506 0z"/> \
                    </svg>';
var icon_check = '<svg class="bi bi-check text-success" width="2.2em" height="2.2em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"> \
                        <path fill-rule="evenodd" d="M10.97 4.97a.75.75 0 0 1 1.071 1.05l-3.992 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.236.236 0 0 1 .02-.022z" /> \
                    </svg>'
var icon_uncheck = '<svg class="bi bi-exclamation text-danger" width="2.2em" height="2.2em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"> \
                        <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z" /> \
                    </svg>'

$('.collapse-btn').click(function () {
    $(this).parents('.form-group').find('[id ^= priceDetail]').collapse('toggle');
});

$('[id ^= priceDetail]').on('shown.bs.collapse', function () {
    $(this).parents('.form-group').find('.collapse-btn').html(icon_collapse);
});

$('[id ^= priceDetail]').on('hidden.bs.collapse', function () {
    $(this).parents('.form-row').siblings('.form-row').find('button').html(icon_expand);
});

function set_status(condition, arg) {
    if (condition > 0) {
        arg.html(icon_check);
    } else {
        arg.html(icon_uncheck);
    };
};

function check_status() {
    set_status($('#mainForm #shop_id').val(), $('#mainForm .checkShop'));

    var main_status = true;
    $('.checkTitle').each(function () {
        set_status($(this).parents('.form-group').find('#id').val(), $(this));
        set_status($(this).parents('.form-group').find('.product_id').val(), $(this).parents('.form-group').find('.checkProduct'));
        
        $(this).parents('.form-group').find('.checkPrice').html(icon_uncheck);
        if ($('#mainForm #shop_id').val() == 0) {
            if ($(this).parents('.form-group').find('.product_id').val() == 0) {
                $(this).parents('.form-group').find('.product-price label').text("Не выбран магазин и товар");
            } else {
                $(this).parents('.form-group').find('.product-price label').text("Не выбран магазин");
            };
        } else {
            if ($(this).parents('.form-group').find('.product_id').val() == 0) {
                $(this).parents('.form-group').find('.product-price label').text("Не выбран товар");
            } else {
                set_status($(this).parents('.form-group').find('#price_id').val(), $(this).parents('.form-group').find('.checkPrice'));
            }
        }

        if ($(this).parents('.form-group').find('#id').val() == 0) {
            main_status = false;
        } else {
            $(this).parents('.form-group').find('.collapse').collapse('hide');
        }
        
    });
    $('#mainForm #submit').attr('disabled', !main_status);
};

setTimeout(check_status, 50);

function update_shops() {
    $.get("{{ url_for('purchase.shops') }}", function (data) {
        $('.shop-list').html(data.html);
        $('#ChooseShop').modal('show');
    });
};

$('.choose-shop').click(function () {
    $('.choose-shop-done').attr('id', $(this))
    update_shops();
});

$('.add-shop').click(function () {
    console.log('add-shop');
    $.ajax({
        type: "POST",
        url: "{{ url_for('purchase.shops_add') }}",
        data: $('#addShop').serialize(),
        success: function (data) {
            if (data.status == "ok") {
                update_shops();
            };
            $('.shop-message').html(data.text);
        },
        error: function (error) {
            console.log(error);
        }
    });
});

$('.choose-shop-done').click(function () {
    var id = $('#ChooseShop .active').attr('id');
    console.log("Shop " + id);
    if (id) {
        $('.shop-name').text("Магазин: " + $('#ChooseShop .active').text());
        $('#mainForm #shop_id').val(id);
        $('[id ^= priceDetail').each(function () {
            $(this).find('#price_id').val('0');
            $(this).find('.product-price label').text('Цена не выбрана');
        });
        check_status();
        $('#ChooseShop').modal('hide');
    } else {
        $('.shop-message').html("Магазин не выбран");
    };
});

$('#ChooseShop .shop-list').on('dblclick', function() {
    $('.choose-shop-done').click();
});

function update_products(val=0) {
    $.get("{{ url_for('catalog.products') }}", function (data) {
        $("#ChooseProduct .product-list").html(data.html);
        $("#ChooseProduct #catalog_id").find('option').remove();
        $("#ChooseProduct #catalogSelect option").clone().appendTo("#ChooseProduct #catalog_id");
        if (val>0) {
            $("#ChooseProduct #catalogSelect").val(val).change();
        };
        $("#ChooseProduct").modal("show");
    });
};

$('.product-name-btn').click(function (event) {
    event.preventDefault();
    $('#addProduct #name').val($(this).parents('.list-group-item').find('.product_name').val());
    $('.choose-product-done').attr('for', $(this).parents('.collapse').attr('id'));
    $('.product-message').html("");
    update_products();
});

$('.add-product').click(function () {
    console.log('add-product');
    $.ajax({
        type: "POST",
        url: "{{ url_for('catalog.add_product') }}",
        data: $('#addProduct').serialize(),
        success: function (data) {
            if (data.status == "ok") {
                var val =$("#ChooseProduct #catalog_id").val();
                update_products(val);
                $('#addProduct').trigger("reset");
            };
            $('.product-message').html(data.text);
        },
        error: function (error) {
            console.log(error);
        }
    });
});

$('.choose-product-done').click(function () {
    var id = $('#ChooseProduct .active').attr('id');
    console.log("Product " + id);
    if (id) {
        var forward = '#' + $(this).attr('for');
        $(forward).find('[for = product_id]').text($('#ChooseProduct .active').text());
        $(forward).find('#product_id').val($('#ChooseProduct .active').attr('id'));
        $(forward).parents('.form-group').find('#title').val($('#ChooseProduct .active').text() + " (Цена не выбрана)");
        $(forward).find('#price_id').val('0');
        $(forward).find('[for = price_id]').text('Цена не выбрана');
        check_status();
        $('#ChooseProduct').modal('hide');
    } else {
        $('.product-message').html("Товар не выбран");
    };
});

$('#ChooseProduct .product-list').on('dblclick', function() {
    $('.choose-product-done').click();
});

function update_prices(product_id) {
    var shop_id = $('#mainForm #shop_id').val();
    var csrf_token = "{{ csrf_token() }}";
    $.ajax({
        type: "POST",
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        },
        url: "{{ url_for('catalog.prices') }}",
        data: {
            'product_id': product_id,
            'shop_id': shop_id
        },
        success: function (data) {
            $('.price-list').html(data.html);
            $('#ChoosePrice #shopSelect option').clone().appendTo('#ChoosePrice #shop_id');
            $("#ChoosePrice #shop_id").val($('#ChoosePrice #shopSelect').val()).change();
            $('#ChoosePrice #productSelect option').clone().appendTo('#ChoosePrice #product_id');
            $('#ChoosePrice #product_id').val($('#ChoosePrice #productSelect').val());
            $('#ChoosePrice').modal('show');
        },
        error: function (error) {
            console.log(error);
        }
    });
};

$('.product-price-btn').click(function () {
    event.preventDefault();
    $('#ChoosePrice #date').val($('#mainForm #date').val().slice(0, 10));
    $('#ChoosePrice #price').val($(this).parents('.list-group-item').find('.price_value').val());
    $('#ChoosePrice #discount').prop('checked', false);;
    $('.choose-price-done').attr('for', $(this).parents('.collapse').attr('id'));
    $('.price-message').html("");
    update_prices($(this).parents('ul').find('.product_id').val());
});

$('.add-price').click(function () {
    console.log('add-price');
    $("#ChoosePrice #shop_id").prop('disabled', false);
    $("#ChoosePrice #product_id").prop("disabled", false);
    $.ajax({
        type: "POST",
        url: "{{ url_for('catalog.add_price') }}",
        data: $('#addPrice').serialize(),
        success: function (data) {
            if (data.status == "ok") {
                update_prices($("#ChoosePrice #product_id").val());
                $('#addPrice').trigger("reset");
            };
            $('.price-message').html(data.text);
        },
        error: function (error) {
            console.log(error);
        }
    });
    $("#ChoosePrice #shop_id").prop('disabled', true);
    $("#ChoosePrice #product_id").prop("disabled", true);
});

$('.choose-price-done').click(function () {
    var id = $('#ChoosePrice .active').attr('id');
    console.log("Price " + id);
    if (id) {
        var forward = '#' + $(this).attr('for');
        var price = $('#ChoosePrice .active');
        $(forward).find('[for = price_id]').text("Цена: " + price.text());
        $(forward).find('#price_id').val(price.attr('id'));
        $(forward).parents('.form-group').find('#id').val(price.attr('id'));
        var product_title = $(forward).find('[for = product_id]').text();
        var price_value = $(forward).find('#price_value').val()
        $(forward).parents('.form-group').find('#title').val(product_title + " (" + price_value + ")");
        check_status();
        $('#ChoosePrice').modal('hide');
    } else {
        $('.price-message').html("Цена не выбрана");
    };
});

$('#ChoosePrice .price-list').on('dblclick', function() {
    $('.choose-price-done').click();
});

$('#submit').click(function (event) {
    event.preventDefault();
    var data = {
        'date': $('#mainForm #date').val(),
        'process_id': $('#mainForm #process_id').val(),
        'shop_id': $('#mainForm #shop_id').val(),
        'total': $('#mainForm .purchase-total #total').val(),
        'items': []
    }
    $('[id ^= priceDetail]').each(function () {
        var price_id = $(this).parents('.form-group').find('#id').val();
        var quantity = $(this).parents('.form-group').find('#quantity').val();
        var total = $(this).parents('.form-group').find('#total').val();
        console.log(price_id + ' - ' + quantity + ' - ' + total);
        data['items'].push({'price_id': price_id, 'quantity': quantity, 'total': total});
    });
    console.log(data);
    var csrf_token = "{{ csrf_token() }}";
    $.ajax({
        type: "POST",
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        },
        contentType: "application/json; charset=utf-8",
        url: "{{ url_for('purchase.confirm') }}",
        data: JSON.stringify(data),
        dataType: "json",
        success: function (data) {
            console.log(data);
            location.href = "{{ url_for('purchase.index') }}";
        },
        error: function (error) {
            console.log(error);
        }
    });
});