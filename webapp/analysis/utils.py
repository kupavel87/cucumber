from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pandas

from webapp.catalog.models import Product
from webapp.purchase.models import Purchase, Purchase_Item

colors = ['#ffa500', '#0000ce', '#00ce00', '#ffff40', '#40ffff', '#ff40ff', '#ff4000', '#8080a5', '#808040', '#5da5a1']


def Age_to_array(age):
    if age == '0':
        return [d.strftime('%d.%m.%Y') for d in pandas.date_range(date.today() + relativedelta(weeks=-1), date.today())]
    if age == '1':
        return [d.strftime('%d.%m.%Y') for d in pandas.date_range(date.today() + relativedelta(months=-1), date.today())]
    if age == '2':
        return [d.strftime('%d.%m.%Y') for d in pandas.date_range(date.today() + relativedelta(months=-6), date.today())]
    if age == '3':
        return [d.strftime('%d.%m.%Y') for d in pandas.date_range(date.today() + relativedelta(years=-1), date.today())]
    return [d.strftime('%d.%m.%Y') for d in pandas.date_range(date.today() + relativedelta(years=-5), date.today())]


def Dataset_for_product(product_id, date_array, user_id, color_id=0, label=None):
    start = datetime.strptime(date_array[0], '%d.%m.%Y')
    purshases = Purchase_Item.query.filter(Purchase_Item.purchase.has(
        author_id=user_id), Purchase_Item.purchase.has(Purchase.date >= start))
    items = purshases.filter(Purchase_Item.price.has(product_id=product_id)).all()
    pre_data = {item.purchase.date.strftime('%d.%m.%Y'): item.quantity for item in items}
    data = [pre_data.get(item, None) for item in date_array]
    if not label:
        label = Product.query.filter_by(id=product_id).first().name
    return {'label': label, 'data': data, 'backgroundColor': colors[color_id % 10]}


def Dateset_for_catalog(catalog_id, date_array, user_id):
    products = Product.query.filter_by(catalog_id=catalog_id).all()
    result = []
    for i, item in enumerate(products):
        result.append(Dataset_for_product(item.id, date_array, user_id, color_id=i, label=item.name))
    return result
