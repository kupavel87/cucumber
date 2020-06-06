from datetime import timedelta
import os


basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, '..', 'webapp.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.environ.get('SECRET_KEY') or 'wooCh,a%efupah>ngifoo6Ku0aeMeep6'

REMEMBER_COOKIE_DURATION = timedelta(days=5)

NALOG_USER = os.environ.get('NALOG_USER') or 'mobile'
NALOG_PASSWORD = os.environ.get('NALOG_PASSWORD') or 'password'

TEMP_DIR = os.environ.get('TEMP_DIR') or os.path.join(basedir, '..', 'temp')

BROKER_URL = os.environ.get('CELERY_BROCKER_URL') or 'redis://localhost'
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379'

MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
MAIL_PORT = os.environ.get('MAIL_PORT') or 587
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'user@gmail.com'
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'password'
