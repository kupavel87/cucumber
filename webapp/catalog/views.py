from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequestKeyError

from webapp.catalog.forms import CreateCatalog, CreateProduct, CreatePrice, CreatePenNameForm
from webapp.catalog.models import Catalog, Product, Price, Pen_name
from webapp.catalog.utils import CatalogModel_for_select, Products_to_Dict
from webapp.db import db
from webapp.purchase.models import Shop, Purchase_Item
from webapp.user.decorators import admin_required
from flask_login import login_required

blueprint = Blueprint('catalog', __name__, url_prefix='/catalog')


@blueprint.route('/')
def index():
    title = 'Каталог товаров'
    return render_template('catalog/index.html', page_title=title)


@blueprint.route('/show')
def show():
    catalog = Catalog.query.filter_by(parent_id=None)
    html = render_template('catalog/catalog.html', catalog=catalog)
    return jsonify({"html": html})


@blueprint.route('/edit/', defaults={'id': 0}, methods=['GET', 'POST'])
@blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    form = CreateCatalog()
    catalog = Catalog.query.filter_by(parent_id=None).all()
    choises = [(0, 'Нет родителя')]
    if len(catalog):
        choises.extend(CatalogModel_for_select(catalog))
    form.parent_id.choices = choises
    if id > 0:
        catalog = Catalog.query.filter_by(id=id).first()
        if request.method == 'GET':
            form.id.data = catalog.id
            form.name.data = catalog.name
            form.parent_id.data = catalog.parent_id
        if request.method == 'POST':
            catalog.name = form.name.data
            if form.parent_id.data == '0':
                catalog.parent_id = None
                catalog.level = 0
            else:
                catalog.parent_id = form.parent_id.data
                catalog.level = None
            text = "Каталог {} изменен".format(catalog.name)
            try:
                db.session.commit()
            except IntegrityError:
                return jsonify(status='error', text="Ошибка")
            return jsonify(status='ok', text=text)
    else:
        if request.method == 'POST':
            new_catalog = Catalog(name=form.name.data, parent_id=form.parent_id.data, level=None)
            if form.parent_id.data == '0':
                new_catalog.parent_id = None
                category.level = 0
            db.session.add(new_catalog)
            text = "Создан каталог {}".format(new_catalog.name)
            try:
                db.session.commit()
            except IntegrityError:
                return jsonify(status='error', text="Ошибка")
            return jsonify(status='ok', text=text)
    html = render_template('catalog/edit.html', form=form)
    return jsonify(html=html)


@blueprint.route('/delete/<int:id>')
@admin_required
def delete(id):
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
    catalog = Catalog.query.filter_by(parent_id=None).all()
    choises = []
    if len(catalog):
        choises.extend(CatalogModel_for_select(catalog))
    form.catalog_id.choices = choises
    if form.validate():
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


@blueprint.route('/product_edit/', defaults={'id': 0}, methods=['GET', "POST"])
@blueprint.route('/product_edit/<int:id>', methods=['GET', "POST"])
@admin_required
def product_edit(id):
    catalog = Catalog.query.filter_by(parent_id=None).all()
    choises = [(0, 'Каталог не выбран')]
    if len(catalog):
        choises.extend(CatalogModel_for_select(catalog))
    form = CreateProduct()
    form.catalog_id.choices = choises
    if id > 0:
        product = Product.query.filter_by(id=id).first()
        if request.method == 'GET':
            form.id.data = product.id
            form.name.data = product.name
            form.code.data = product.code
            form.catalog_id.data = product.catalog_id
        if request.method == 'POST' and form.validate_on_submit():
            if product:
                product.name = form.name.data
                product.code = None if form.code.data == '' else form.code.data
                product.catalog_id = form.catalog_id.data
                text = 'Изменения товара {} сохранены.'.format(product.name)
                try:
                    db.session.commit()
                except IntegrityError:
                    return jsonify(status='error', text='Ошибка. Товар {} уже существует.'.format(product.name))        
                return jsonify(status='ok', text=text)
            return jsonify(status='error', text='Ошибка. Товар не найден.')
    html = render_template('catalog/product_edit.html', form=form)
    return jsonify(html=html)


@blueprint.route('/product_delete/<int:id>')
@admin_required
def product_delete(id):
    product = Product.query.filter_by(id=id).first()
    if not product:
        return jsonify(status='error', text="Ошибка. Продукт не найден.")
    product.pen_names.delete()
    product.prices.delete()
    db.session.delete(product)
    text = "Удален товар {}.".format(product.name)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text="Ошибка. Этот продукт встречается в чеках.")
    return jsonify(status='ok', text=text)


@blueprint.route('/pen_name_edit/', defaults={'id': 0}, methods=['GET', "POST"])
@blueprint.route('/pen_name_edit/<int:id>', methods=['GET', "POST"])
@admin_required
def pen_name_edit(id):
    catalog = Catalog.query.filter_by(parent_id=None).all()
    choises = [(0, 'Каталог не выбран')]
    if len(catalog):
        choises.extend(CatalogModel_for_select(catalog))
    form = CreatePenNameForm()
    form.catalog_id.choices = choises
    products = Products_to_Dict(Product.query.all(), True)
    if request.method == 'GET' and id > 0:
        selected = Pen_name.query.filter_by(id=id).first()
        form.id.data = selected.id
        form.name.data = selected.name
        form.catalog_id.data = selected.product.catalog_id
        form.product_id.choices = products[form.catalog_id.data]
        form.product_id.data = selected.product_id

    if request.method == 'POST':
        form.product_id.choices = products[int(request.form.get('catalog_id'))]
        if form.validate_on_submit():
            if id > 0:
                pen_name = Pen_name.query.filter_by(id=id).first()
                if pen_name:
                    pen_name.name = form.name.data
                    pen_name.product_id = form.product_id.data
                    db.session.commit()
                    return jsonify(status='ok')
            return jsonify(status='error')
    html = render_template('catalog/pen_name_edit.html', form=form, products=products)
    return jsonify(html=html)


@blueprint.route('/pen_name_delete/<int:id>')
@admin_required
def pen_name_delete(id):
    pen_name = Pen_name.query.filter_by(id=id).first()
    if not pen_name:
        return jsonify(status='error', text="Ошибка. Псевдоним не найден")
    db.session.delete(pen_name)
    text = "Удален псевдоним {}.".format(pen_name.name)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text="Ошибка.")
    return jsonify(status='ok', text=text)


@blueprint.route('/price_edit/', defaults={'id': 0}, methods=['GET', "POST"])
@blueprint.route('/price_edit/<int:id>', methods=['GET', "POST"])
@admin_required
def price_edit(id):
    catalog = Catalog.query.filter_by(parent_id=None).all()
    choises = [(0, 'Каталог не выбран')]
    if len(catalog):
        choises.extend(CatalogModel_for_select(catalog))
    form = CreatePrice()
    form.catalog_id.choices = choises
    products = Products_to_Dict(Product.query.all(), True)
    shops = [(shop.id, shop.name) for shop in Shop.query.all()]
    form.shop_id.choices = shops
    if request.method == 'GET' and id > 0:
        selected = Price.query.filter_by(id=id).first()
        form.id.data = selected.id
        form.catalog_id.data = selected.product.catalog_id
        form.product_id.choices = products[form.catalog_id.data]
        form.product_id.data = selected.product_id
        form.date.data = selected.date
        form.price.data = selected.price
        form.discount.data = selected.discount
    if request.method == 'POST':
        form.product_id.choices = products[int(request.form.get('catalog_id'))]
        if form.validate_on_submit():
            if id > 0:
                price = Price.query.filter_by(id=id).first()
                if price:
                    price.product_id = form.product_id.data
                    price.shop_id = form.shop_id.data
                    price.date = form.date.data
                    price.price = form.price.data
                    price.discount = form.discount.data
                    db.session.commit()
                    return jsonify(status='ok', text='Изменение цены сохранено.')
            return jsonify(status='error', text='Ошибка изменения цены.')
    html = render_template('catalog/price_edit.html', form=form, products=products)
    return jsonify(html=html)


@blueprint.route('/price_delete/<int:id>')
@admin_required
def price_delete(id):
    price = Price.query.filter_by(id=id).first()
    if not price:
        return jsonify(status='error', text="Ошибка. Цена не найдена.")
    db.session.delete(price)
    text = "Удалена цена {}.".format(price.price)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text="Ошибка. Эта цена встречается в чеках.")
    return jsonify(status='ok', text=text)
