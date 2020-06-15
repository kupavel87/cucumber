from flask import Blueprint, flash, render_template, redirect, url_for, jsonify, request
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from webapp.db import db
from webapp.celery.tasks import send_password_reset_email, send_confirm_registration_email
from webapp.user.decorators import admin_required
from webapp.user.forms import LoginForm, RegistrationForm, EditUser, ChangePassword, ResetPasswordRequestForm, ResetPasswordForm
from webapp.user.models import User
from webapp.user.utils import random_password


blueprint = Blueprint('user', __name__, url_prefix='/user')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Вы уже авторизованы на сайте')
        return redirect(url_for('purchase.index'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('Вы успешно вошли на сайт')
                return redirect(url_for('purchase.index'))
        else:
            flash('Неправильные имя или пароль')
            return redirect(url_for('user.login'))
    return render_template('user/login.html', form=form)


@blueprint.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно разлогинились')
    return redirect(url_for('purchase.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('purchase.index'))
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(username=form.username.data, email=form.email.data, role='user')
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Вы успешно зарегистрировались! Для получения полного доступа к сайту, вам на почту отправлено письмо с инструкцией. Проверьте вашу почту!')
            send_confirm_registration_email.delay(new_user)
            return redirect(url_for('user.login'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash('Ошибка в поле "{}": - {}'.format(getattr(form, field).label.text, error))
            return redirect(url_for('user.register'))
    return render_template('user/registration.html', form=form)


@blueprint.route('/register/<token>')
def confirm_register(token):
    user = User.verify_token(token)
    if not user:
        flash('Ошибка. Обратитесь к администратору.')
        return redirect(url_for('main.index'))
    user.limit_access = False
    db.session.commit()
    if not current_user.is_authenticated:
        login_user(user)
    flash('Регистрация подтверждена.')
    return redirect(url_for('main.index'))


@blueprint.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email.delay(user)
        flash('Инструкция по сбросу пароля отправлена вам на почту.')
        return redirect(url_for('user.login'))
    return render_template('user/reset_password_request.html', form=form)


@blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password2(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_token(token)
    if not user:
        flash('Ошибка. Обратитесь к администратору.')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Пароль успешно изменен.')
        return redirect(url_for('user.login'))
    return render_template('user/reset_password.html', form=form)


@blueprint.route('/edit/', defaults={'id': 0}, methods=['GET', 'POST'])
@blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    form1 = EditUser()
    form2 = ChangePassword(prefix="pass")
    if id > 0:
        user = User.query.filter_by(id=id).first()
        if request.method == 'GET':
            form1.id.data = user.id
            form1.username.data = user.username
            form1.email.data = user.email
            form1.role.data = user.role
            form2.id.data = user.id
        if request.method == 'POST':
            if form1.validate_on_submit():
                user.username = form1.username.data
                user.email = form1.email.data
                user.role = form1.role.data
                text = "Пользователь {} изменен".format(user.username)
            elif form2.validate_on_submit():
                user.set_password(form2.password.data)
                text = "Пароль пользователя {} изменен".format(user.username)
            else:
                return jsonify(status='error', text='{}'.format(form1.errors))
            try:
                db.session.commit()
            except IntegrityError:
                text = "Ошибка сохранения пользователя {}".format(user.username)
                return jsonify(status='error', text=text)
            return jsonify(status='ok', text=text)
    else:
        if form1.validate_on_submit():
            new_user = User(username=form1.username.data, email=form1.email.data, role=form1.role.data)
            new_pass = random_password()
            new_user.set_password(new_pass)
            db.session.add(new_user)
            try:
                db.session.commit()
            except IntegrityError:
                text = "Ошибка сохранения пользователя {}".format(form1.username.data)
                return jsonify(status='error', text=text)
            text = "Пользователь {} добавлен. Пароль {}".format(form1.username.data, new_pass)
            return jsonify(status='ok', text=text)
    html = render_template('user/edit.html', form1=form1, form2=form2)
    return jsonify(html=html)


@blueprint.route('/delete/<int:id>')
@admin_required
def delete(id):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    text = 'Пользователь {} удален'.format(user.username)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text='Ошибка удаления пользователя {}'.format(user.username))
    return jsonify(status='ok', text=text)
