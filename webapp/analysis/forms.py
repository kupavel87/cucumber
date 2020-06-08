from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, DateField, HiddenField, SelectField, FieldList, FormField, IntegerField, FloatField
from wtforms.validators import DataRequired

ages = [(0, 'за неделю'), (1, 'за месяц'), (2, 'за полгода'), (3, 'за год'), (4, 'за все время')]


class SelcetDataForm(FlaskForm):
    age = SelectField('Период данных', choices=ages, coerce=int, validators=[
                      DataRequired()], render_kw={"class": "form-control"})
    catalog = SelectField('Период данных', coerce=int, validators=[DataRequired()], render_kw={"class": "form-control"})
    product = IntegerField('product_id', render_kw={"class": "form-control", "hidden": ""})
    submit = SubmitField('Показать', render_kw={"class": "btn btn-lg btn-danger btn-block"})
