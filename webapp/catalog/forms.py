from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, DateTimeField, HiddenField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired


class CreateCatalog(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    name = StringField('Название', render_kw={"class": "form-control"})
    parent_id = SelectField('Родитель', coerce=int, render_kw={"class": "form-control"})
