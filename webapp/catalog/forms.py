from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, DateField, HiddenField, SelectField, FieldList, FormField, IntegerField, FloatField
from wtforms.validators import DataRequired


class CreateCatalog(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    name = StringField('Название', render_kw={"class": "form-control"})
    parent_id = SelectField('Родитель', coerce=int, render_kw={"class": "form-control"})


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
            # self.name = shop.name
            # self.address = shop.address


class CreateProduct(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    name = StringField('Название', validators=[DataRequired()], render_kw={"class": "form-control"})
    code = StringField('Штрих-код', render_kw={"class": "form-control"})
    catalog_id = SelectField('Каталог', coerce=int, render_kw={"class": "form-control"})
    pen_name = StringField('Псевдоним', render_kw={"class": "form-control"})


class CreatePrice(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    shop_id = SelectField('Магазин', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    product_id = SelectField('Товар', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    date = DateField('Дата', validators=[DataRequired()], format='%d.%m.%Y', render_kw={"class": "form-control"})
    price = FloatField('Сумма', validators=[DataRequired()], render_kw={"class": "form-control"})
    discount = BooleanField('Акционная цена', default=True, render_kw={'class': 'form-check-input'})
