from datetime import datetime
import json
import requests

from flask import current_app as app
from sqlalchemy import desc

# from webapp.config import nalog_user, nalog_password
from webapp.catalog.models import Product, Price, Pen_name
from webapp.purchase.models import Shop, Cash_desk

check_url = 'https://proverkacheka.nalog.ru:9999/v1/ofds/*/inns/*/fss/{fn}/operations/1/tickets/{fd}?fiscalSign={fp}&date={fdate}&sum={fsum}'
detail_url = 'https://proverkacheka.nalog.ru:9999/v1/inns/*/kkts/*/fss/{fn}/tickets/{fd}?fiscalSign={fp}&sendToEmail=no'
translate = {'fn': 'fn', 'fp': 'fp', 'i': 'fd', 't': 'fdate', 's': 'fsum'}


def parser_answer(file):
    with open(file, 'r', encoding='utf-8') as json_file:
        answer = json.load(json_file)
    date = datetime.strptime(answer['document']['receipt'].get('dateTime'), '%Y-%m-%dT%H:%M:%S')
    total = answer['document']['receipt'].get('totalSum') / 100
    shop_inn = answer['document']['receipt'].get('userInn')
    fn = answer['document']['receipt'].get('fiscalDriveNumber')
    shop_address = answer['document']['receipt'].get('retailPlaceAddress')
    items = answer['document']['receipt'].get('items')

    shop = ''
    if fn:
        cash_desk = Cash_desk.query.filter_by(fn=fn)
        if cash_desk.count() == 1:
            shop = cash_desk.first().shop
    if not shop and shop_inn:
        shop_by_inn = Shop.query.filter_by(inn=shop_inn)
        if shop_by_inn.count() == 1:
            shop = shop_by_inn.first()
    if not shop and shop_address:
        shop_by_address = Shop.query.filter_by(address=shop_address)
        if shop_by_address.count() == 1:
            shop = shop_by_address.first()
        else:
            shop = Shop(inn=shop_inn, address=shop_address)
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
        if not product:
            pen_name = Pen_name.query.filter_by(name=name).first()
            if pen_name:
                product = pen_name.product

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


def check_voucher(fn, fd, fp, fdate, fsum):
    headers = {"Device-Id": 'none', "Device-OS": 'Adnroid 5.1',
               'Version': '2', 'ClientVersion': '1.4.5', 'User-Agent': 'okhttp/3.0.1'}
    s = requests.Session()
    url = check_url.format(fn=fn, fd=fd, fp=fp, fdate=fdate, fsum=fsum)
    answer = s.get(url, headers=headers, auth=(app.config['NALOG_USER'], app.config['NALOG_PASSWORD']),)
    return answer.status_code


def get_voucher(fn, fd, fp):
    headers = {"Content-Type": "application/json; charset=UTF-8", "Device-Id": 'none',
               "Device-OS": 'Adnroid 5.1', 'Version': '2', 'ClientVersion': '1.4.5', 'User-Agent': 'okhttp/3.0.1'}
    s = requests.Session()
    url = detail_url.format(fn=fn, fd=fd, fp=fp)
    answer = s.get(url, headers=headers, auth=(app.config['NALOG_USER'], app.config['NALOG_PASSWORD']),)
    if answer.status_code == 200:
        return answer.json()
    print(answer.status_code)
    return False


def parser_QR(qr_str):
    result = {}
    list_arguments = qr_str.split('&')
    for item in list_arguments:
        key, value = item.split('=')
        key = translate.get(key, '')
        if key:
            result[key] = value
    result['fsum'] = result['fsum'].replace('.', '')
    if len(result) == len(translate):
        return result
    return None
