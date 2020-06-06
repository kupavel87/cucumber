from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequestKeyError

from webapp.catalog.forms import CreateCatalog, CreateProduct, CreatePrice
from webapp.catalog.models import Catalog, Product, Price, Pen_name
from webapp.db import db
from webapp.purchase.models import Shop
from webapp.user.decorators import admin_required
from flask_login import login_required

blueprint = Blueprint('catalog', __name__, url_prefix='/catalog')


def CatalogModel_for_select(catalog):
    result = []
    for item in catalog:
        prefix = '--' * item.get_level()
        result.append((item.id, '{}{}'.format(prefix, item.name)))
        children = item.children.all()
        if len(children):
            result.extend(CatalogModel_for_select(children))
    return result


def Products_to_Dict(products):
    result = {}
    for item in products:
        prod = {'id': item.id, 'name': item.name.replace('\"', '\''), 'code': item.code}
        id = item.catalog_id
        if id in result:
            result[id].append(prod)
        else:
            result[id] = [prod]
    return result


@blueprint.route('/')
def index():
    title = 'Каталог товаров'
    return render_template('catalog/index.html', page_title=title)


@blueprint.route('/show')
def show():
    catalog = Catalog.query.filter_by(parent_id=None)
    html = render_template('catalog/catalog.html', catalog=catalog)
    return jsonify({"html": html})


@blueprint.route('/get/', defaults={'category_id': 0})
@blueprint.route('/get/<int:category_id>')
@admin_required
def get(category_id):
    catalog = Catalog.query.filter_by(parent_id=None).all()
    choises = [(0, 'Нет родителя')]
    if len(catalog):
        choises.extend(CatalogModel_for_select(catalog))
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
        text = "Изменен каталог {}".format(name)
    else:
        if parent_id != '0':
            new_category = Catalog(name=name, parent_id=parent_id)
        else:
            new_category = Catalog(name=name, parent_id=None, level=0)
        db.session.add(new_category)
        text = "Создан каталог {}".format(name)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text="Ошибка")
    return jsonify(status='ok', text=text)


@blueprint.route('/delete', methods=['POST'])
@admin_required
def delete():
    id = request.form['id']
    category = Catalog.query.filter_by(id=id).first()
    text = "Удален каталог {}".format(category.name)
    db.session.delete(category)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text="Ошибка")
    return jsonify(status='ok', text=text)


@blueprint.route('/products')
@login_required
def products():
    all_products = Products_to_Dict(Product.query.all())
    catalog = Catalog.query.filter_by(parent_id=None).all()
    choises = [(0, 'Не выбран')]
    if len(catalog):
        choises.extend(CatalogModel_for_select(catalog))
    html = render_template('catalog/products.html', all_products=all_products, choises=choises)
    return jsonify(html=html)


@blueprint.route('/add_product', methods=['POST'])
@login_required
def add_product():
    form = CreateProduct()
    print(request.form)
    catalog = Catalog.query.filter_by(parent_id=None).all()
    choises = []
    if len(catalog):
        choises.extend(CatalogModel_for_select(catalog))
    form.catalog_id.choices = choises
    if form.validate():
        print('Good')
        if form.id.data:
            pass
        else:
            new_product = Product(name=form.name.data, code=form.code.data or None, catalog_id=form.catalog_id.data)
            db.session.add(new_product)
            text = "Добавлен товар {}".format(new_product.name)
        try:
            db.session.commit()
        except IntegrityError:
            return jsonify(status='error', text="Ошибка: Товар {} уже существует".format(new_product.name))
        if form.pen_name.data:
            new_pen_name = Pen_name(product_id=new_product.id, name=form.pen_name.data)
            db.session.add(new_pen_name)
            text += ". Добавлен псевдоним {}".format(new_pen_name.name)
        try:
            db.session.commit()
        except IntegrityError:
            return jsonify(status='error', text="Ошибка: Товар {} добавлен. Псевдоним {} уже существует".format(new_product.name, new_pen_name.name))
        return jsonify(status="ok", text=text)
    return jsonify(status="error", text="Ошибка данных")


@blueprint.route('/prices', methods=['POST'])
@login_required
def prices():
    try:
        product_id = request.form['product_id']
        shop_id = request.form['shop_id']
    except BadRequestKeyError:
        return jsonify(html="<h2>Ошибка данных</h2>")
    shop = Shop.query.filter_by(id=shop_id).first()
    product = Product.query.filter_by(id=product_id).first()
    prices = Price.query.filter_by(product_id=product_id, shop_id=shop_id).all()
    html = render_template('catalog/prices.html', shop=shop, product=product, prices=prices)
    return jsonify(html=html)


@blueprint.route('/add_price', methods=['POST'])
@login_required
def add_price():
    form = CreatePrice()
    # shop_choises = []
    # for shop in Shop.query.all():
    #     shop_choises.append((shop.id, shop.name))
    # form.shop_id.choices = shop_choises
    # product_choises = []
    # for product in Product.query.all():
    #     product_choises.append((product.id, product.name))
    # form.product_id.choices = product_choises
    try:
        shop_id = int(request.form['shop_id'])
        product_id = int(request.form['product_id'])
    except BadRequestKeyError:
        return jsonify(status='error', text="Ошибка данных")
    form.shop_id.choices = [(shop_id, shop_id)]
    form.product_id.choices = [(product_id, product_id)]
    if form.validate():
        if form.id.data:
            pass
        else:
            new_price = Price(date=form.date.data, product_id=form.product_id.data,
                              shop_id=form.shop_id.data, price=form.price.data, discount=form.discount.data)
            db.session.add(new_price)
            text = "Добавлена цена {}".format(new_price.price)
        try:
            db.session.commit()
        except IntegrityError:
            return jsonify(status='error', text="Ошибка: Цена {} уже существует".format(new_price.price))
        return jsonify(status="ok", text=text)
    return jsonify(status="error", text="Ошибка формы")
