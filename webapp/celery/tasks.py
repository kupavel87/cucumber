import json
import os

from celery import Celery
from flask import current_app as app
from flask import render_template

from webapp.celery.utils import check_voucher, get_voucher
from webapp.db import db
from webapp.email import send_email
from webapp.purchase.models import Process_Purchase

celery = Celery(__name__, config_source='webapp.config')


@celery.task
def Check_Voucher(process_id):
    process = Process_Purchase.query.filter_by(id=process_id).first()
    if process:
        status_code = check_voucher(fn=process.fn, fd=process.fd, fp=process.fp, fdate=process.fdate, fsum=process.fsum)
        print("Check voucher id={}, status code={}".format(process.id, status_code))
        if status_code == 204:
            process.attempt = 1
            Get_Voucher_Detail.apply_async([process_id], countdown=10)
        else:
            process.attempt = process.max_attempt
        db.session.commit()


@celery.task
def Get_Voucher_Detail(process_id):
    process = Process_Purchase.query.filter_by(id=process_id).first()
    if process:
        if os.path.isfile(process.link):
            return
        if process.attempt < process.max_attempts:
            answer = get_voucher(fn=process.fn, fd=process.fd, fp=process.fp)
            print("Voucher id={}, get detail={}, attempt={}".format(process.id, bool(answer), process.attempt))
            if answer:
                with open(process.link, 'w', encoding='utf-8') as f:
                    json.dump(answer, f)
                process.attempt = -1
            else:
                process.attempt += 1
                Get_Voucher_Detail.apply_async([process_id], countdown=10)
            db.session.commit()


@celery.task
def send_password_reset_email(user):
    token = user.get_token()
    send_email('[Cucumber] Сброс пароля', sender=app.config['MAIL_USERNAME'], recipients=[user.email],
               text_body=render_template('email/reset_password.html', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))


@celery.task
def send_confirm_registration_email(user):
    token = user.get_token(expires_in=86400)
    send_email('[Cucumber] Подтверждение регистрации', sender=app.config['MAIL_USERNAME'], recipients=[user.email],
               text_body=render_template('email/registration.html', user=user, token=token),
               html_body=render_template('email/registration.html', user=user, token=token))
