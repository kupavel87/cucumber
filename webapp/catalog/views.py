from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify

from webapp.catalog.models import Catalog
from webapp.db import db

blueprint = Blueprint('catalog', __name__, url_prefix='/catalog')


@blueprint.route('/')
def index():
    title = 'Каталог товаров'
    return render_template('catalog/index.html', page_title=title)
    # return render_template('purchase/index.html', page_title=title)


@blueprint.route('/show')
def show():
    catalog = Catalog.query.filter_by(parent_id=None)
    html = render_template('catalog/catalog.html', catalog=catalog)
    return jsonify({"html": html})
