from flask import Flask, flash, render_template, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect

from webapp.db import db
from webapp.admin.views import blueprint as admin_blueprint
from webapp.analysis.views import blueprint as analysis_blueprint
from webapp.catalog.views import blueprint as catalog_blueprint
from webapp.celery.tasks import celery
from webapp.email import mail
from webapp.main.views import blueprint as main_blueprint
from webapp.purchase.views import blueprint as purchase_blueprint
from webapp.shopping.views import blueprint as shopping_blueprint
from webapp.user.models import User
from webapp.user.views import blueprint as user_blueprint


def make_celery(app, celery):
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.jinja_options['extensions'].append('jinja2.ext.do')
    db.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db)
    moment = Moment(app)
    CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(analysis_blueprint)
    app.register_blueprint(catalog_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(purchase_blueprint)
    app.register_blueprint(shopping_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    return app
