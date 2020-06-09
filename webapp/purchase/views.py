from datetime import datetime
import os

from flask import Blueprint, abort, flash, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from webapp.catalog.forms import CreateProduct, CreatePrice
from webapp.db import db
from webapp.purchase.forms import AddVoucherForm, AddVoucherQRForm, CreateShop, VoucherConfirm, VoucherRow
from webapp.purchase.models import Purchase, Purchase_Item, Process_Purchase, Cash_desk, Shop
from webapp.celery.utils import parser_answer, parser_QR
from webapp.celery.tasks import Check_Voucher

blueprint = Blueprint('purchase', __name__, url_prefix='/purchase')


@blueprint.route('/')
@login_required
def index():
    # processes = Process_Purchase.query.filter_by(author_id=current_user.id).all()
    # return render_template('purchase/index.html', processes=current_user.processes, purchases=current_user.purchases)
    return render_template('purchase/index2.html', user=current_user)


@blueprint.route('/shops')
@login_required
def shops():
    shops = Shop.query.all()
    html = render_template('purchase/shops.html', shops=shops)
    return jsonify(html=html)


@blueprint.route('/shops/add', methods=['POST'])
@login_required
def shops_add():
    form = CreateShop()
    if form.validate():
        if form.id.data:
            pass
        else:
            new_shop = Shop(name=form.name.data, address=form.address.data, inn=form.inn.data)
            db.session.add(new_shop)
            text = "Добавлен магазин {}".format(new_shop.name)
        try:
            db.session.commit()
        except IntegrityError:
            return jsonify(status='error', text="Ошибка: Магазин {} уже существует".format(new_shop.name))
        return jsonify(status="ok", text=text)
    return jsonify(status="error", text="Ошибка данных")


@blueprint.route('/process/add', methods=['GET', 'POST'])
@login_required
def process_add():
    form = AddVoucherForm()
    form2 = AddVoucherQRForm()
    if form.validate_on_submit():
        process = Process_Purchase.query.filter_by(fp=form.fp.data).first()
        if not process:
            process = Process_Purchase(author_id=current_user.id, fn=form.fn.data, fd=form.fd.data,
                                       fp=form.fp.data, fdate=form.fdate.data.strftime('%Y-%m-%dT%H:%M'), fsum=form.fsum.data, attempt=0)
            db.session.add(process)
        else:
            process.update(form.fn.data, form.fd.data, form.fdate.data.strftime('%Y-%m-%dT%H:%M'), form.fsum.data)
        db.session.commit()
        Check_Voucher.delay(process_id=process.id)
        return redirect(url_for('purchase.waiting', fp=process.fp))
    if form2.validate_on_submit():
        parser_data = parser_QR(form2.qr_str.data)
        process = Process_Purchase.query.filter_by(fp=parser_data['fp']).first()
        if not process:
            process = Process_Purchase(author_id=current_user.id, fn=parser_data['fn'], fd=parser_data['fd'],
                                       fp=parser_data['fp'], fdate=parser_data['fdate'], fsum=parser_data['fsum'], attempt=0)
            db.session.add(process)
            db.session.commit()
        Check_Voucher.delay(process_id=process.id)
        return redirect(url_for('purchase.waiting', fp=process.fp))
    flash("ЧТо-то пошло не так")
    return render_template('purchase/add.html', form=form, form2=form2)


@blueprint.route('/process/edit/', defaults={'fp': ''})
@blueprint.route('/process/edit/<fp>')
@login_required
def process_edit(fp):
    process = Process_Purchase.query.filter_by(fp=fp).first() if fp else False
    if process and process.is_edit(current_user):

        form = AddVoucherForm(fn=process.fn, fd=process.fd, fp=process.fp,
                              fdate=datetime.strptime(process.fdate, '%Y-%m-%d %H:%M'), fsum=process.fsum)
        html = render_template('purchase/pre_add.html', form=form)
    else:
        form = AddVoucherForm()
        form2 = AddVoucherQRForm()
        html = render_template('purchase/pre_add.html', form=form, form2=form2)
    return jsonify(html=html)


@blueprint.route('/waiting/<fp>')
@login_required
def waiting(fp):
    process = Process_Purchase.query.filter_by(fp=fp).first()
    if process.is_edit(current_user):
        status = process.status()
        if status == 'ok':
            if os.path.isfile(process.link):
                date, total, shop, products = parser_answer(process.link)
                form3 = VoucherConfirm(process_id=process.id, date=date, total=total, shop=shop, products=products)
                shop_form = CreateShop(shop=shop)
                product_form = CreateProduct()
                price_form = CreatePrice()
                return render_template('purchase/add_confirm2.html', form=form3, shop_form=shop_form, product_form=product_form, price_form=price_form,
                                       date=date, total=total, shop=shop, products=products)
            else:
                status = 'error'
                process.attempt = process.max_attempts
                db.session.commit()
        if status == 'error':
            return render_template('purchase/error.html', process=process)
        return render_template('purchase/waiting.html', status=status)
    abort(404)


@blueprint.route('/repeat/<fp>')
@login_required
def repeat(fp):
    process = Process_Purchase.query.filter_by(fp=fp).first()
    if process.is_edit(current_user):
        if os.path.isfile(process.link):
            os.remove(process.link)
        process.attempt = 0
        db.session.commit()
        Check_Voucher.delay(process_id=process.id)
        return redirect(url_for('purchase.waiting', fp=process.fp))
    abort(404)


@blueprint.route('/confirm', methods=['POST'])
@login_required
def confirm():
    form = request.json
    process = Process_Purchase.query.filter_by(id=form['process_id']).first()
    if process:
        old_purchase = Purchase.query.filter_by(fp=process.fp).count()
        if not old_purchase:
            new_purchase = Purchase(date=datetime.strptime(form['date'], '%d.%m.%Y %H:%M'), fp=process.fp,
                                    shop_id=form['shop_id'], total=form['total'], author_id=current_user.id)
            db.session.add(new_purchase)
            db.session.commit()
            for item in form['items']:
                new_purchase_item = Purchase_Item(purchase_id=new_purchase.id, price_id=item['price_id'],
                                                  quantity=item['quantity'], total=item['total'])
                db.session.add(new_purchase_item)
            cash_desk = Cash_desk.query.filter_by(fn=process.fn).count()
            if not cash_desk:
                cash_desk = Cash_desk(shop_id=form['shop_id'], fn=process.fn)
                db.session.add(cash_desk)
            db.session.commit()
            os.remove(process.link)
            db.session.delete(process)
            db.session.commit()
            flash("Добавлен чек {} на сумму {} из магазина {}".format(
                new_purchase.fp, new_purchase.total, new_purchase.shop.name))
            return jsonify(status='ok')
    flash("Ошибка добавления чека")
    return jsonify(status='error')


@blueprint.route('/detail/<int:id>')
@login_required
def detail(id):
    purchase = Purchase.query.filter_by(id=id).first()
    if purchase.is_edit(current_user):
        html = render_template('purchase/detail.html', purchase=purchase)
        return jsonify(status='ok', html=html)
    return jsonify(status='error')
