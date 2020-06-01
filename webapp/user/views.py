import random
import string

from flask import Blueprint, flash, render_template, redirect, url_for, jsonify, request
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from webapp.db import db
from webapp.user.decorators import admin_required
from webapp.user.forms import LoginForm, RegistrationForm, EditUser, ChangePassword
from webapp.user.models import User


blueprint = Blueprint('user', __name__, url_prefix='/user')


def random_password(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


@blueprint.route('/login')
def login():
    if current_user.is_authenticated:
        flash('Вы уже авторизованы на сайте')
        return redirect(url_for('purchase.index'))

    title = ''
    login_form = LoginForm()
    return render_template('user/login.html', page_title=title, form=login_form)


@blueprint.route('/process-login', methods=['POST'])
def process_login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Вы успешно вошли на сайт')
            return redirect(url_for('purchase.index'))

    flash('Неправильные имя или пароль')
    return redirect(url_for('user.login'))


@blueprint.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно разлогинились')
    return redirect(url_for('purchase.index'))


@blueprint.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('purchase.index'))
    title = ''
    form = RegistrationForm()
    return render_template('user/registration.html', page_title=title, form=form)


@blueprint.route('/process-reg', methods=['POST'])
def process_reg():
    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, role='user')
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!')
        return redirect(url_for('user.login'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash('Ошибка в поле "{}": - {}'.format(getattr(form, field).label.text, error))
        return redirect(url_for('user.regist'))


@blueprint.route('/get/', defaults={'id': 0})
@blueprint.route('/get/<int:id>')
@admin_required
def get(id):
    form1 = EditUser()
    form2 = ChangePassword()
    if id > 0:
        user = User.query.filter_by(id=id).first()
        form1.load(user)
        form2.id.data = user.id
    html = render_template('user/get.html', form1=form1, form2=form2)
    return jsonify(html=html)


@blueprint.route('/save', methods=['POST'])
@admin_required
def save():
    form = EditUser()
    if form.id.data:
        user = User.query.filter_by(id=form.id.data).first()
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
    else:
        new_user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        new_pass = random_password()
        new_user.set_password(new_pass)
        db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        text = "Ошибка сохранения пользователя {}".format(form.username.data)
        return jsonify(status='error', text=text)
    if form.id.data:
        text = "Пользователь {} изменен".format(form.username.data)
    else:
        text = "Пользователь {} добавлен. Пароль {}".format(form.username.data, new_pass)
    return jsonify(status='ok', text=text)


@blueprint.route('/change_pass', methods=['POST'])
@admin_required
def change_pass():
    form = ChangePassword()
    print(request.form)
    if form.validate:
        user = User.query.filter_by(id=form.id.data).first()
        user.set_password(form.password.data)
        try:
            db.session.commit()
        except IntegrityError:
            text = "Ошибка сохранения пользователя {}".format(user.username)
            return jsonify(status='error', text=text)
        text = "Пароль пользователя {} изменен".format(user.username)
        return jsonify(status='ok', text=text)
    return jsonify(status='error', text="Ошибка данных")


@blueprint.route('/delete', methods=['POST'])
@admin_required
def delete():
    id = request.form['id']
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text='Ошибка удаления пользователя {}'.format(user.username))
    return jsonify(status='ok', text='Пользователь {} удален'.format(user.username))
