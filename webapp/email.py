from flask import current_app as app
from flask import render_template
from flask_mail import Mail, Message

mail = Mail()


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_token()
    send_email('[Cucumber] Сброс пароля', sender=app.config['MAIL_USERNAME'], recipients=[user.email],
               text_body=render_template('email/reset_password.html', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))


def send_confirm_registration_email(user):
    token = user.get_token()
    # print("Send mail. token={}".format(token))
    send_email('[Cucumber] Подтверждение регистрации', sender=app.config['MAIL_USERNAME'], recipients=[user.email],
               text_body=render_template('email/registration.html', user=user, token=token),
               html_body=render_template('email/registration.html', user=user, token=token))
