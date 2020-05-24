from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify

from webapp.purchase.forms import AddVoucherForm
from webapp.db import db

blueprint = Blueprint('purchase', __name__)


@blueprint.route('/')
def index():
    title = 'Список покупок'
    form = AddVoucherForm()
    return render_template('purchase/index.html', page_title=title, form=form)
    # return render_template('purchase/index.html', page_title=title)


@blueprint.route('/add_voucher', methods=['POST'])
def add_voucher():
    title = '123'
    return render_template('purchase/index.html', page_title=title)
