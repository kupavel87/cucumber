from flask import Flask, flash, render_template, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from flask_migrate import Migrate
from flask_moment import Moment

from webapp.db import db
from webapp.catalog.models import Catalog
from webapp.catalog.views import blueprint as catalog_blueprint
from webapp.purchase.models import Purchase
from webapp.purchase.views import blueprint as purchase_blueprint
from webapp.shopping.models import Shopping_list
from webapp.shopping.views import blueprint as shopping_blueprint
from webapp.user.models import User
from webapp.user.views import blueprint as user_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.jinja_options['extensions'].append('jinja2.ext.do')
    db.init_app(app)
    migrate = Migrate(app, db)
    moment = Moment(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    app.register_blueprint(user_blueprint)
    app.register_blueprint(catalog_blueprint)
    app.register_blueprint(purchase_blueprint)
    app.register_blueprint(shopping_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    return app
