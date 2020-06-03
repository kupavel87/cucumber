from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateTimeField, DecimalField, BooleanField, TextAreaField, IntegerField, FieldList, FormField, FloatField, Label, Form
from wtforms.validators import DataRequired
from wtforms import validators

from webapp.catalog.models import Product, Price


class CreateShop(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    inn = StringField('ИНН', render_kw={"class": "form-control"})
    name = StringField('Название', validators=[DataRequired()], render_kw={"class": "form-control"})
    address = StringField('Адрес', render_kw={"class": "form-control"})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        shop = kwargs.pop('shop', '')
        if shop and not shop.id:
            self.inn.data = shop.inn
            self.name.data = shop.name
            self.address.data = shop.address


class AddVoucherForm(FlaskForm):
    fn = StringField('fn', validators=[DataRequired()], render_kw={"class": "form-control"})
    fd = StringField('fd', validators=[DataRequired()], render_kw={"class": "form-control"})
    fp = StringField('fp', validators=[DataRequired()], render_kw={"class": "form-control"})
    fdate = DateTimeField('Дата', format='%Y-%m-%dT%H:%M',
                          validators=[DataRequired()], render_kw={"class": "form-control"})
    fsum = StringField('Сумма', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-success btn-block"})


class AddVoucherQRForm(FlaskForm):
    qr_str = TextAreaField('QR код', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-success btn-block"})


class VoucherRow(FlaskForm):
    id = StringField('id', validators=[DataRequired()], render_kw={"class": "form-control", "hidden": ""})
    title = StringField('Товар + Цена', validators=[DataRequired()],
                        render_kw={"class": "form-control", "readonly": ""})
    product_id = StringField('Товар--', validators=[DataRequired()],
                             render_kw={"class": "form-control product_id", "hidden": ""})
    product_name = StringField('Название товара', validators=[DataRequired()], render_kw={
                               "class": "form-control product_name", "hidden": ""})
    price_id = StringField('Цена', validators=[DataRequired()], render_kw={"class": "form-control", "hidden": ""})
    price_value = FloatField('Цена', validators=[DataRequired()], render_kw={
                             "class": "form-control price_value", "hidden": ""})
    quantity = FloatField('Количество', validators=[DataRequired()], render_kw={
                          "class": "form-control text-center", "readonly": ""})
    total = FloatField('Сумма', validators=[DataRequired()], render_kw={
                       "class": "form-control text-center", "readonly": ""})

    def __init__(self, product=Product(), price=Price(), quantity=0.0, total=0.0, **kwargs):
        super().__init__(**kwargs)
        self.id.data = '0'
        self.title.data = 'Необходимо выбрать товар и цену'
        self.quantity.data = quantity
        self.total.data = total
        if product and product.id:
            self.product_id.data = product.id
            self.product_id.label.text = product.name
            if price and price.id:
                self.price_id.label.text = "Цена: {} ({})".format(price.price, price.date.strftime('%d-%m-%Y'))
                self.price_id.data = price.id
                self.id.data = price.id
                self.title.data = "{} ({})".format(product.name, price.price)
            else:
                self.price_id.data = '0'
                self.price_id.label.text = 'Цена не выбрана'
                self.title.data = "{} ({})".format(product.name, "Цена не выбрана")
        else:
            self.product_id.label.text = "Товар не выбран"
            self.price_id.label.text = "Цена не выбрана"
            self.product_id.data = "0"
            self.price_id.data = "0"
        self.price_value.data = price.price
        self.product_name.data = product.name


class VoucherConfirm(FlaskForm):
    process_id = StringField('id', validators=[DataRequired()], render_kw={"class": "form-control", "hidden": ""})
    date = DateTimeField('Дата:', format='%d.%m.%Y %H:%M', validators=[
                         DataRequired()], render_kw={"class": "form-control"})
    shop_id = StringField('Выберите магазин', validators=[DataRequired()],
                          render_kw={"class": "form-control", "hidden": ""})
    total = FloatField('Сумма:', validators=[DataRequired()], render_kw={
                       "class": "form-control text-center", "readonly": ""})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-success btn-block"})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date.data = kwargs.pop('date', '')
        self.total.data = kwargs.pop('total', 0)
        self.shop_id.data = '0'
        self.shop_id.label.text = 'Выберите магазин'
        shop = kwargs.pop('shop', '')
        if shop and shop.id:
            self.shop_id.data = shop.id
            self.shop_id.label.text = "Магазин: {}".format(shop.name)
        products = kwargs.pop('products', [])
        if products:
            self.rows = []
            for item in products:
                row = VoucherRow(product=item['product'], price=item['price'],
                                 quantity=item['quantity'], total=item['total'])
                self.rows.append(row)
