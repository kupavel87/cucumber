from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequestKeyError

from webapp.admin.forms import UserForm
from webapp.catalog.models import Catalog, Product, Pen_name, Price
from webapp.purchase.models import Purchase, Purchase_Item, Shop, Cash_desk, Process_Purchase
from webapp.shopping.models import Shopping_list, List_access, Shopping_item
from webapp.user.decorators import admin_required
from webapp.user.models import User
from webapp.db import db

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

chapters = {
    'users': {'name': 'Пользователи', 'link': 'admin.users'},
    'catalog': {'name': 'Каталог', 'link': 'admin.catalog'},
    'products': {'name': 'Продукты', 'link': 'admin.products'},
    'pen_names': {'name': 'Пседонимы продуктов', 'link': 'admin.pen_names'},
    'prices': {'name': 'Цены', 'link': 'admin.prices'},
    'shops': {'name': 'Магазины', 'link': 'admin.shops'},
    'cash_desks': {'name': 'Кассы', 'link': 'admin.cash_desks'},
    'purchases': {'name': 'Чеки', 'link': 'admin.purchases'},
    'purchase_items': {'name': 'Детали чеков*', 'link': 'admin.purchase_items'},
    'process_purchases': {'name': 'Обработка чеков*', 'link': 'admin.process_purchases'},
    'shopping_list': {'name': 'Списки покупок', 'link': 'admin.shopping_list'},
    'shopping_items': {'name': 'Детали списков покупок*', 'link': 'admin.shopping_items'},
    'list_access': {'name': 'Права достпа к спискам покупок*', 'link': 'admin.coming_soon'},
}


@blueprint.route('/')
@admin_required
def index():
    title = 'Админка'
    return render_template('admin/index2.html', page_title=title, chapters=chapters)


@blueprint.route('/coming_soon')
@admin_required
def coming_soon():
    html = render_template('admin/coming_soon.html')
    return jsonify(html=html)


@blueprint.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    users = User.query.all()
    if request.method == 'GET':
        html = render_template('admin/users.html', users=users)
    else:
        try:
            id = request.form['id']
            btn = request.form['btn']
        except BadRequestKeyError:
            return "Error. Id not found."
        if btn == 'self':
            shopping_list = Shopping_list.query.filter_by(author_id=id).all()
        elif btn == 'available':
            available_list = List_access.query.filter_by(user_id=id).all()
            available_list = [item.list_id for item in available_list]
            shopping_list = Shopping_list.query.filter(Shopping_list.id.in_(available_list)).all()
        else:
            return "Error. Button not found."
        html = render_template('admin/shopping_list.html', shopping_list=shopping_list)
    return jsonify(html=html)


@blueprint.route('/catalog')
@admin_required
def catalog():
    catalog = Catalog.query.filter_by(parent_id=None)
    html = render_template('admin/catalog.html', catalog=catalog)
    return jsonify(html=html)


@blueprint.route('/products/', defaults={'id': 0})
@blueprint.route('/products/<int:id>')
@admin_required
def products(id):
    if id > 0:
        products = Product.query.filter_by(catalog_id=id).all()
    else:
        products = Product.query.all()
    html = render_template('admin/products.html', products=products)
    return jsonify(html=html)


@blueprint.route('/pen_names')
@admin_required
def pen_names():
    pen_names = Pen_name.query.order_by(Pen_name.product_id).all()
    html = render_template('admin/pen_names.html', pen_names=pen_names)
    return jsonify(html=html)


@blueprint.route('/prices')
@admin_required
def prices():
    prices = Price.query.order_by(Price.product_id).all()
    html = render_template('admin/prices.html', prices=prices)
    return jsonify(html=html)


@blueprint.route('/shops')
@admin_required
def shops():
    shops = Shop.query.all()
    html = render_template('admin/shops.html', shops=shops)
    return jsonify(html=html)


@blueprint.route('/cash_desks')
@admin_required
def cash_desks():
    cash_desks = Cash_desk.query.all()
    html = render_template('admin/cash_desks.html', cash_desks=cash_desks)
    return jsonify(html=html)


@blueprint.route('/purchases')
@admin_required
def purchases():
    purchases = Purchase.query.all()
    html = render_template('admin/purchases.html', purchases=purchases)
    return jsonify(html=html)


@blueprint.route('/purchase_items/', defaults={'id': 0})
@blueprint.route('/purchase_items/<int:id>')
@admin_required
def purchase_items(id):
    if id > 0:
        purchase_items = Purchase_Item.query.filter_by(purchase_id=id).all()
    else:
        purchase_items = Purchase_Item.query.all()
    html = render_template('admin/purchase_items.html', items=purchase_items)
    return jsonify(html=html)


@blueprint.route('/process_purchases/')
@admin_required
def process_purchases():
    process_purchases = Process_Purchase.query.all()
    html = render_template('admin/process_purchases.html', items=process_purchases)
    return jsonify(html=html)


@blueprint.route('/shopping_list')
@admin_required
def shopping_list():
    shopping_list = Shopping_list.query.all()
    html = render_template('admin/shopping_list.html', shopping_list=shopping_list)
    return jsonify(html=html)


@blueprint.route('/shopping_items')
@admin_required
def shopping_items():
    shopping_items = Shopping_item.query.all()
    html = render_template('admin/shopping_items.html', shopping_items=shopping_items)
    return jsonify(html=html)
