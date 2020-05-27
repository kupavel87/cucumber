from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify
from sqlalchemy.exc import IntegrityError

from webapp.catalog.forms import CreateCatalog
from webapp.catalog.models import Catalog
from webapp.db import db
from webapp.user.decorators import admin_required

blueprint = Blueprint('catalog', __name__, url_prefix='/catalog')


def CatalogModel_to_Dict(catalog):
    result = []
    for item in catalog:
        prefix = '--' * item.get_level()
        result.append((item.id, '{}{}'.format(prefix, item.name)))
        children = item.children.all()
        if len(children):
            result.extend(CatalogModel_to_Dict(children))
    return result


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


@blueprint.route('/get/<int:category_id>')
@admin_required
def get(category_id):
    catalog = Catalog.query.filter_by(parent_id=None).all()
    choises = [(0, 'Нет родителя')]
    if len(catalog):
        choises.extend(CatalogModel_to_Dict(catalog))
    form = CreateCatalog()
    form.parent_id.choices = choises
    if category_id > 0:
        selected = Catalog.query.filter_by(id=category_id).first()
        form.id.data = selected.id
        form.name.data = selected.name
        form.parent_id.data = selected.parent_id
    html = render_template('catalog/get.html', form=form)
    return jsonify(html=html)


@blueprint.route('/save', methods=['POST'])
@admin_required
def save():
    id = request.form['id']
    parent_id = request.form['parent_id']
    name = request.form['name']
    if id:
        category = Catalog.query.filter_by(id=id).first()
        category.name = name
        if parent_id != '0':
            category.parent_id = parent_id
        else:
            category.parent_id = None
            category.level = 0
    else:
        if parent_id != '0':
            new_category = Catalog(name=name, parent_id=parent_id)
        else:
            new_category = Catalog(name=name, parent_id=None, level=0)
        db.session.add(new_category)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error')
    return jsonify(status='ok')


@blueprint.route('/delete', methods=['POST'])
@admin_required
def delete():
    id = request.form['id']
    category = Catalog.query.filter_by(id=id).first()
    db.session.delete(category)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error')
    return jsonify(status='ok')
