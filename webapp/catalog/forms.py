from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, DateField, HiddenField, SelectField, FieldList, FormField, IntegerField, FloatField
from wtforms.validators import DataRequired


class CreateCatalog(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    name = StringField('Название', render_kw={"class": "form-control"})
    parent_id = SelectField('Родитель', coerce=int, render_kw={"class": "form-control"})
    submit = SubmitField('Сохранить', render_kw={"class": "btn btn-success"})


class CreateProduct(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    name = StringField('Название', validators=[DataRequired()], render_kw={"class": "form-control"})
    code = StringField('Штрих-код', render_kw={"class": "form-control"})
    catalog_id = SelectField('Каталог', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    pen_name = StringField('Псевдоним', render_kw={"class": "form-control"})
    submit = SubmitField('Сохранить', render_kw={"class": "btn btn-success"})


class CreatePrice(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    catalog_id = SelectField('Каталог', coerce=int, render_kw={"class": "form-control"})
    product_id = SelectField('Товар', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    shop_id = SelectField('Магазин', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    date = DateField('Дата', validators=[DataRequired()], format='%d.%m.%Y', render_kw={"class": "form-control"})
    price = FloatField('Сумма', validators=[DataRequired()], render_kw={"class": "form-control"})
    discount = BooleanField('Акционная цена', default=False, render_kw={'class': 'form-check-input'})
    submit = SubmitField('Сохранить', render_kw={"class": "btn btn-success"})


class CreatePenNameForm(FlaskForm):
    id = IntegerField('id', default=0, render_kw={"class": "form-control", "hidden": ""})
    catalog_id = SelectField('Каталог', coerce=int, render_kw={"class": "form-control"})
    product_id = SelectField('Товар', coerce=int, render_kw={"class": "form-control"})
    name = StringField('Псевдоним', render_kw={"class": "form-control"})
    submit = SubmitField('Сохранить', render_kw={"class": "btn btn-success"})
