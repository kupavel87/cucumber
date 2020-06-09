import os

from webapp.celery.tasks import celery
from webapp import create_app, make_celery

app = create_app()

with app.app_context():
    make_celery(app, celery)
