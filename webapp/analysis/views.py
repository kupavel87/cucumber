from datetime import datetime
import json

from flask import Blueprint, flash, render_template, jsonify, request
from flask_login import login_required, current_user

from webapp.analysis.forms import SelcetDataForm
from webapp.analysis.utils import Age_to_array, Dataset_for_product, Dateset_for_catalog
from webapp.catalog.models import Catalog, Product, Price
from webapp.catalog.utils import CatalogChildrenCount, CatalogModel_for_select, Products_to_Dict
from webapp.purchase.models import Purchase, Purchase_Item
from webapp.db import db
from webapp.purchase.models import Shop

blueprint = Blueprint('analysis', __name__, url_prefix='/analysis')


@blueprint.route('/')
def index():
    catalog_top = Catalog.query.filter_by(parent_id=None).all()
    catalog_products_count = {}
    CatalogChildrenCount(catalog_top, catalog_products_count)
    catalog_select = CatalogModel_for_select(catalog_top, catalog_products_count)
    form = SelcetDataForm()
    catalog_select.insert(0, (0, 'Не выбран'))
    form.catalog.choices = catalog_select
    products = Products_to_Dict(Product.query.all())
    return render_template('analysis/index.html', form=form, products=products)


@blueprint.route('/load_data', methods=['POST'])
@login_required
def load_data():
    form = request.form
    product_id = form.get('product', 0)
    catalog_id = form.get('catalog', 0)
    age = form.get('age', 0)
    labels = Age_to_array(age)
    dataset = []
    if product_id and product_id != "0":
        dataset.append(Dataset_for_product(product_id, labels, current_user.id))
    elif catalog_id and catalog_id != "0":
        dataset.extend(Dateset_for_catalog(catalog_id, labels, current_user.id))
    else:
        return jsonify(status='error')
    return jsonify(status='ok', labels=labels, dataset=json.dumps(dataset))
