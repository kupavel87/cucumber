from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateTimeField, DecimalField, BooleanField
from wtforms.validators import DataRequired


class AddCatalogForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()], render_kw={"class": "form-control"})
    parent = SelectField('Родитель', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-primary btn-block"})


class AddProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()], render_kw={"class": "form-control"})
    catalog = SelectField('Категория', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-primary btn-block"})


class AddShopForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-primary btn-block"})


class AddPriceForm(FlaskForm):
    date = DateTimeField('Дата', format='%d.%m.%Y %H:%M', validators=[DataRequired()], render_kw={"class": "form-control"})
    product = SelectField('Продукт', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    price = DecimalField('Цена', use_locale=True, validators=[DataRequired()], render_kw={"class": "form-control"})
    shop = SelectField('Магазин', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    discont = BooleanField('Скидка', false_values=None, validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-primary btn-block"})


class AddPurchaseForm(FlaskForm):
    date = DateTimeField('Дата', format='%d.%m.%Y %H:%M', validators=[DataRequired()], render_kw={"class": "form-control"})
    price = SelectField('Цена', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    number = DecimalField('Количество', use_locale=True, validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-primary btn-block"})


class AddVoucherForm(FlaskForm):
    fn = StringField('fn', validators=[DataRequired()], render_kw={"class": "form-control"})
    fd = StringField('fd', validators=[DataRequired()], render_kw={"class": "form-control"})
    fp = StringField('fp', validators=[DataRequired()], render_kw={"class": "form-control"})
    fdate = StringField('Дата', validators=[DataRequired()], render_kw={"class": "form-control"})
    fsum = StringField('Сумма', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-primary btn-block"})


class AddVoucherQRForm(FlaskForm):
    st = StringField('QR код', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Добавить', render_kw={"class": "btn btn-lg btn-primary btn-block"})
