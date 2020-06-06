import os

from webapp.celery.tasks import celery
from webapp import create_app, make_celery

try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    load_dotenv(os.path.join(basedir, '.env'))

app = create_app()

with app.app_context():
    make_celery(app, celery)
