from datetime import datetime
import os

from flask import Blueprint, abort, flash, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from webapp.catalog.forms import CreateProduct, CreatePrice
from webapp.db import db
from webapp.catalog.models import Price
from webapp.catalog.utils import Prices_to_Dict
from webapp.celery.utils import parser_answer, parser_QR
from webapp.celery.tasks import Check_Voucher
from webapp.purchase.forms import AddVoucherForm, AddVoucherQRForm, CreateShop, VoucherConfirm, VoucherRow, CreateCashDeskForm, CreatePurchaseForm, CreatePurchaseItemForm
from webapp.purchase.models import Purchase, Purchase_Item, Process_Purchase, Cash_desk, Shop
from webapp.purchase.utils import Purchase_to_Dict
from webapp.user.decorators import admin_required
from webapp.user.models import User

blueprint = Blueprint('purchase', __name__, url_prefix='/purchase')


@blueprint.route('/')
@login_required
def index():
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


@blueprint.route('/shop_edit/', defaults={'id': 0}, methods=['GET', 'POST'])
@blueprint.route('/shop_edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def shop_edit(id):
    form = CreateShop()
    if request.method == 'GET' and id > 0:
        shop = Shop.query.filter_by(id=id).first()
        form.id.data = shop.id
        form.name.data = shop.name
        form.inn.data = shop.inn
        form.address.data = shop.address
    if request.method == 'POST' and form.validate_on_submit():
        if id > 0:
            shop = Shop.query.filter_by(id=id).first()
            if shop:
                shop.name = form.name.data
                shop.inn = form.inn.data
                shop.address = form.address.data
                db.session.commit()
                return jsonify(status='ok', text='Изменение магазина сохранено.')
        return jsonify(status='error', text='Ошибка изменения магазина.')
    html = render_template('purchase/shop_edit.html', form=form)
    return jsonify(html=html)


@blueprint.route('/shop_delete/<int:id>')
@admin_required
def shop_delete(id):
    shop = Shop.query.filter_by(id=id).first()
    if not shop:
        return jsonify(status='error', text='Ошибка. Магазин не найден.')
    db.session.delete(shop)
    text = 'Удален магазин {}.'.format(shop.name)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text="Ошибка. Этот магазин встречается в чеках.")
    return jsonify(status='ok', text=text)


@blueprint.route('/cash_desk_edit/', defaults={'id': 0}, methods=['GET', 'POST'])
@blueprint.route('/cash_desk_edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def cash_desk_edit(id):
    form = CreateCashDeskForm()
    shops = [(s.id, s.name) for s in Shop.query.all()]
    choises = [(0, 'Магазин не выбран')]
    if len(shops):
        choises.extend(shops)
    form.shop_id.choices = choises
    if request.method == 'GET' and id > 0:
        cash_desk = Cash_desk.query.filter_by(id=id).first()
        form.id.data = cash_desk.id
        form.shop_id.data = cash_desk.shop_id
        form.fn.data = cash_desk.fn
    if request.method == 'POST' and form.validate_on_submit():
        if id > 0:
            cash_desk = Cash_desk.query.filter_by(id=id).first()
            cash_desk.shop_id = form.shop_id.data
            cash_desk.fn = form.fn.data
            db.session.commit()
            return jsonify(status='ok', text='Изменение кассы сохранено.')
        return jsonify(status='error', text='Ошибка изменения кассы.')
    html = render_template('purchase/cash_desk_edit.html', form=form)
    return jsonify(html=html)


@blueprint.route('/cash_desk_delete/<int:id>')
@admin_required
def cash_desk_delete(id):
    cash_desk = Cash_desk.query.filter_by(id=id).first()
    if not cash_desk:
        return jsonify(status='error', text='Ошибка. Касса не найдена.')
    db.session.delete(cash_desk)
    text = 'Удалена касса {}.'.format(cash_desk.fn)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text="Ошибка.")
    return jsonify(status='ok', text=text)


@blueprint.route('/purchase_edit/', defaults={'id': 0}, methods=['GET', 'POST'])
@blueprint.route('/purchase_edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def purchase_edit(id):
    form = CreatePurchaseForm()
    shops = [(s.id, s.name) for s in Shop.query.all()]
    choises = [(0, 'Магазин не выбран')]
    if len(shops):
        choises.extend(shops)
    form.shop_id.choices = choises
    users = [(u.id, u.username) for u in User.query.all()]
    choises = [(0, 'Пользователь не выбран')]
    choises.extend(users)
    form.author_id.choices = choises
    if request.method == 'GET' and id > 0:
        purhcase = Purchase.query.filter_by(id=id).first()
        form.id.data = purhcase.id
        form.date.data = purhcase.date
        form.fp.data = purhcase.fp
        form.shop_id.data = purhcase.shop_id
        form.author_id.data = purhcase.author_id
        form.total.data = purhcase.total
    if request.method == 'POST' and form.validate_on_submit():
        if id > 0:
            purhcase = Purchase.query.filter_by(id=id).first()
            purhcase.date = form.date.data
            purhcase.fp = form.fp.data
            purhcase.shop_id = form.shop_id.data
            purhcase.author_id = form.author_id.data
            purhcase.total = form.total.data
            db.session.commit()
            return jsonify(status='ok', text='Изменение чека сохранено.')
    html = render_template('purchase/purchase_edit.html', form=form)
    return jsonify(html=html)


@blueprint.route('/purchase_delete/<int:id>')
@admin_required
def purchase_delete(id):
    purchase = Purchase.query.filter_by(id=id).first()
    if not purchase:
        return jsonify(status='error', text='Ошибка. Чек не найден.')
    db.session.delete(purchase)
    text = 'Удален чек {}.'.format(purchase.fp)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text="Ошибка.")
    return jsonify(status='ok', text=text)


@blueprint.route('/purchase_item_edit/', defaults={'id': 0}, methods=['GET', 'POST'])
@blueprint.route('/purchase_item_edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def purchase_item_edit(id):
    # form = CreatePurchaseItemForm()
    # users = [(u.id, u.username) for u in User.query.all()]
    # choises = [(0, 'Пользователь не выбран')]
    # choises.extend(users)
    # form.author_id.choices = choises
    # purchases = Purchase_to_Dict(Purchase.query.all())
    # prices = Prices_to_Dict(Price.query.all())
    # print(prices)
    # if request.method == 'GET' and id > 0:
    #     purchase_item = Purchase_Item.query.filter_by(id=id).first()
    #     form.purchase_id.choices = purchases[form.author_id.data]
    #     form.purchase_id.data = purhcase_item.purchase_id
    #     form.price_id.choices = prices[form.purchase_id.data]
    #     form.price_id.data = purhcase_item.price_id
    #     form.quantity.data = purhcase_item.quantity
    #     form.total.data = purhcase_item.total
    # html = render_template('purchase/purchase_item_edit.html', form=form, purchases=purchases)
    # return jsonify(html=html)
    pass


@blueprint.route('/purchase_item_delete/<int:id>')
@admin_required
def purchase_item_delete(id):
    purchase_item = Purchase_Item.query.filter_by(id=id).first()
    if not purchase_item:
        return jsonify(status='error', text='Ошибка. Чек не найден.')
    db.session.delete(purchase_item)
    text = 'Удален строка {} в чеке.'.format(purchase_item.id, purchase_item.price_id)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status='error', text="Ошибка.")
    return jsonify(status='ok', text=text)


@blueprint.route('/process_purchase_edit/', defaults={'id': 0}, methods=['GET', 'POST'])
@blueprint.route('/process_purchase_edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def process_purchase_edit(id):
    pass


@blueprint.route('/process_purchase_delete/<int:id>')
@admin_required
def process_purchase_delete(id):
    pass
