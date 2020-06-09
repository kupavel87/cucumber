from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequestKeyError

from webapp.admin.forms import UserForm
from webapp.catalog.models import Catalog, Product
from webapp.purchase.models import Purchase, Purchase_Item
from webapp.shopping.models import Shopping_list, List_access
from webapp.user.decorators import admin_required
from webapp.user.models import User
from webapp.db import db

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

chapters = {
    'users': {'name': 'Пользователи', 'link': 'admin.users'},
    'catalog': {'name': 'Каталог', 'link': 'admin.catalog'},
    'products': {'name': 'Продукты', 'link': 'admin.products'},
    'pen_names': {'name': 'Пседонимы продуктов*', 'link': 'admin.index'},
    'prices': {'name': 'Цены*', 'link': 'admin.index'},
    'shops': {'name': 'Магазины*', 'link': 'admin.index'},
    'cash_desks': {'name': 'Кассы*', 'link': 'admin.index'},
    'purchases': {'name': 'Чеки', 'link': 'admin.purchases'},
    'purchase_items': {'name': 'Детали чеков*', 'link': 'admin.index'},
    'process_purchases': {'name': 'Обработка чеков*', 'link': 'admin.index'},
    'shopping_list': {'name': 'Списки покупок', 'link': 'admin.shopping_list'},
    'shopping_items': {'name': 'Детали списков покупок*', 'link': 'admin.index'},
    'list_access': {'name': 'Права достпа к спискам покупок*', 'link': 'admin.index'},
}


@blueprint.route('/')
@admin_required
def index():
    title = 'Админка'
    return render_template('admin/index2.html', page_title=title, chapters=chapters)


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
    html = render_template('admin/catalog3.html', catalog=catalog)
    return jsonify(html=html)


@blueprint.route('/shopping_list')
@admin_required
def shopping_list():
    shopping_list = Shopping_list.query.all()
    html = render_template('admin/shopping_list.html', shopping_list=shopping_list)
    return jsonify(html=html)


@blueprint.route('/products')
@admin_required
def products():
    products = Product.query.all()
    html = render_template('admin/products.html', products=products)
    return jsonify(html=html)


@blueprint.route('/purchases')
@admin_required
def purchases():
    purchases = Purchase.query.all()
    print(purchases)
    html = render_template('admin/purchases.html', purchases=purchases)
    return jsonify(html=html)


@blueprint.route('/purchase_items', methods=['POST'])
@login_required
def purchase_items():
    try:
        id = request.form['id']
    except BadRequestKeyError:
        return "Error. Id not found."
    purchase = Purchase.query.filter_by(id=id).first()
    if current_user.is_admin or current_user.id == purchase.author_id:
        html = render_template('admin/purchase_items.html', items=purchase.items)
    else:
        html = "Ошибка доступа"
    return jsonify(html=html)
