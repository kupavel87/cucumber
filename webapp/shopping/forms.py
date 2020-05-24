from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import DataRequired, ValidationError


class CreateShoppingListForm(FlaskForm):
    name = StringField('Название', default='Новый список', validators=[DataRequired()], render_kw={"class": "form-control", "onClick": "this.select();"})
    favorit = BooleanField('Важный', default=False, render_kw={'class': 'checkbox'})
    private = BooleanField('Личный', default=True, render_kw={'class': 'checkbox'})
