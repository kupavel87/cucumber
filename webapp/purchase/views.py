from datetime import datetime
import json
import os

from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify
from sqlalchemy import desc

from webapp.catalog.forms import CreateShop, CreateProduct, CreatePrice
from webapp.catalog.models import Shop, Product, Price, Pen_name
from webapp.purchase.forms import AddVoucherForm, AddVoucherQRForm, VoucherConfirm, VoucherRow
from webapp.db import db

blueprint = Blueprint('purchase', __name__, url_prefix='/purchase')


def parser_answer(answer):
    date = datetime.strptime(answer['document']['receipt']['dateTime'], '%Y-%m-%dT%H:%M:%S')
    total = answer['document']['receipt']['totalSum'] / 100
    shop_inn = answer['document']['receipt']['userInn']
    items = answer['document']['receipt']['items']

    shop = Shop.query.filter_by(inn=shop_inn).first()
    if not shop:
        shop = Shop(inn=shop_inn)
    products = []
    for item in items:
        name = item['name']
        code = name[:13]
        product = ''
        if code.isnumeric():
            product = Product.query.filter_by(code=code).first()
        if not product:
            product = Product.query.filter_by(name=name).first()
        # if not product:
        #     product = Pen_name.query.filter_by(name=name).first().product

        value = item['price'] / 100
        if product:
            price = Price.query.filter_by(product_id=product.id, shop_id=shop.id, price=value, discount=True).first()
            if not price:
                last_price = Price.query.filter_by(product_id=product.id, shop_id=shop.id,
                                                   discount=False).order_by(desc(Price.date)).first()
                if last_price and last_price.price == value:
                    price = last_price
                else:
                    price = Price(date=date, product_id=product.id, shop_id=shop.id, price=value)
        else:
            product = Product(name=name)
            price = Price(date=date, shop_id=shop.id, price=value)
        products.append({'product': product, 'price': price, 'quantity': item['quantity'], 'total': item['sum'] / 100})

    return date, total, shop, products


@blueprint.route('/')
def index():
    return render_template('purchase/index.html')


@blueprint.route('/add', methods=['GET', 'POST'])
def add():
    form = AddVoucherForm()
    form2 = AddVoucherQRForm()
    if form.validate():
        file_name = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'temp/answer.json'))
        with open(file_name) as json_file:
            answer = json.load(json_file)
        date, total, shop, products = parser_answer(answer)
        form3 = VoucherConfirm(date=date, total=total, shop=shop, products=products)
        shop_form = CreateShop(shop=shop)
        product_form = CreateProduct()
        price_form = CreatePrice()
        return render_template('purchase/add_confirm2.html', form=form3, shop_form=shop_form, product_form=product_form, price_form=price_form,
                               date=date, total=total, shop=shop, products=products)
    return render_template('purchase/add.html', form=form, form2=form2)


@blueprint.route('/confirm', methods=['POST'])
def confirm():
    print(request.json)
    return redirect(url_for('purchase.add'))
