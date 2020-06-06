from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, email_validator
from webapp.user.models import User

roles = [('user', 'Пользователь'), ('admin', 'Администратор')]


def Validate_Username(username):
    users_count = User.query.filter_by(username=username.data).count()
    if users_count > 0:
        raise ValidationError('Пользователь с таким именем уже зарегистрирован')


def Validate_Email(email):
    users_count = User.query.filter_by(email=email.data).count()
    if users_count > 0:
        raise ValidationError('Пользователь с такой электронной почтой уже зарегистрирован')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()], render_kw={"class": "form-control"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"class": "form-control"})
    remember_me = BooleanField('Запомнить меня', default=True, render_kw={'class': 'form-check-input'})
    submit = SubmitField('Отправить!', render_kw={"class": "btn btn-lg btn-primary btn-block"})


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()], render_kw={"class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"class": "form-control"})
    password2 = PasswordField('Повторите пароль', validators=[
                              DataRequired(), EqualTo('password')], render_kw={"class": "form-control"})
    submit = SubmitField('Зарегистрироваться', render_kw={"class": "btn btn-lg btn-success btn-block"})

    def validate_username(self, username):
        return Validate_Username(username)

    def validate_email(self, email):
        return Validate_Email(email)


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    submit = SubmitField('Отправить!', render_kw={"class": "btn btn-lg btn-danger btn-block"})


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"class": "form-control"})
    password2 = PasswordField('Повторите пароль', validators=[
                              DataRequired(), EqualTo('password')], render_kw={"class": "form-control"})
    submit = SubmitField('Поменять пароль', render_kw={"class": "btn btn-lg btn-danger btn-block"})


class EditUser(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    username = StringField('Имя пользователя', validators=[DataRequired()], render_kw={"class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    role = SelectField('Роль', validators=[DataRequired()], choices=roles, render_kw={"class": "form-control"})

    def validate_username(self, username):
        return Validate_Username(username)

    def validate_email(self, email):
        return Validate_Email(email)

    def load(self, user):
        self.id.data = user.id
        self.username.data = user.username
        self.email.data = user.email
        self.role.data = user.role


class ChangePassword(FlaskForm):
    id = StringField('id', render_kw={"class": "form-control", "hidden": ""})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"class": "form-control"})
    password2 = PasswordField('Повторите пароль', validators=[
                              DataRequired(), EqualTo('password')], render_kw={"class": "form-control"})
