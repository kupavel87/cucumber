from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequestKeyError

from webapp.catalog.models import Catalog
from webapp.shopping.forms import CreateShoppingListForm, OpenDetail, DeleteList, RoleForm, ClearList
from webapp.shopping.models import Shopping_list, Shopping_item, List_access
from webapp.user.decorators import admin_required
from webapp.user.models import User
from webapp.db import db

blueprint = Blueprint('shopping', __name__, url_prefix='/shopping')


@blueprint.route('/')
@login_required
def index():
    title = 'Список покупок'
    return render_template('shopping/index2.html', page_title=title)


@blueprint.route('/update_grid')
@login_required
def update_grid():
    my_lists = Shopping_list.query.filter_by(author_id=current_user.get_id())
    shared_lists_id = [item.list_id for item in List_access.query.filter_by(user_id=current_user.get_id()).all()]
    shared_lists = Shopping_list.query.filter(Shopping_list.id.in_(shared_lists_id))
    favorit_lists = my_lists.union(shared_lists).filter_by(favorit=True)

    open_form = OpenDetail()
    del_form = DeleteList()
    html = render_template('shopping/grid.html', my_lists=my_lists.all(), shared_lists=shared_lists.all(),
                           favorit_lists=favorit_lists.all(), open_form=open_form, del_form=del_form)
    return jsonify({'html': html})


@blueprint.route('/create_list', methods=['POST'])
@login_required
def create_list():
    form = CreateShoppingListForm()
    if form.validate_on_submit():
        if form.list_id.data:
            shopping_list = Shopping_list.query.filter_by(id=form.list_id.data).first()
            if shopping_list.check_access(current_user.id) < 4:
                flash('Недостаточно прав для изменения списка {}'.format(form.name.data))
                return redirect(url_for('shopping.index'))
            shopping_list.name = form.name.data
            shopping_list.favorit = form.favorit.data
            shopping_list.private = form.private.data
            shopping_list.access.all().delete()
            flash('Список {} сохранен'.format(form.name.data))
        else:
            shopping_list = Shopping_list(name=form.name.data, favorit=form.favorit.data,
                                          private=form.private.data, author_id=current_user.id)
            db.session.add(shopping_list)
            flash('Список {} создан'.format(form.name.data))

        if not shopping_list.private:
            access = {entry.data['id']: entry.data['role'] for entry in form.access.entries}
            access_users = User.query.filter(User.username.in_(access.keys())).all()
            for user in access_users:
                list_access = List_access(list_id=shopping_list.id, user_id=user.id, role=access.get(user.id, 0))
                db.session.add(list_access)
        db.session.commit()
    return redirect(url_for('shopping.index'))


@blueprint.route('/property_list', methods=['GET', 'POST'])
@login_required
def property_list():
    users = User.query.filter(User.id != current_user.get_id()).all()
    if request.method == 'GET':
        form = CreateShoppingListForm('Новый список', users=users)
    else:
        try:
            id = request.form['id']
        except BadRequestKeyError:
            return "Error. Id not found."
        shopping_list = Shopping_list.query.filter_by(id=id).first()
        if not shopping_list:
            return "Error. Id not found."
        form = CreateShoppingListForm(shopping_list.name, list_id=shopping_list.id, favorit=shopping_list.favorit,
                                      private=shopping_list.private, users=users, access=shopping_list.access_dict())
    html = render_template('shopping/property.html', form=form)
    return jsonify(html=html)


@blueprint.route('/delete_list', methods=['POST'])
@login_required
def delete_list():
    try:
        id = request.form['id']
    except BadRequestKeyError:
        return redirect(url_for('shopping.index'))
    shopping_list = Shopping_list.query.filter_by(id=id).first()
    if shopping_list and shopping_list.check_access(current_user.id) > 3:
        db.session.delete(shopping_list)
        db.session.commit()
    return redirect(url_for('shopping.index'))


@blueprint.route('/detail', methods=['GET', 'POST'])
@login_required
def detail():
    my_lists = Shopping_list.query.filter_by(author_id=current_user.get_id())
    shared_lists_id = [item.list_id for item in List_access.query.filter_by(user_id=current_user.get_id()).all()]
    shared_lists = Shopping_list.query.filter(Shopping_list.id.in_(shared_lists_id))
    favorit_lists = my_lists.union(shared_lists).filter_by(favorit=True)
    if request.method == 'POST':
        try:
            id = request.form['id']
        except BadRequestKeyError:
            return 'Error. Id not found'
        return render_template('shopping/detail.html', my_lists=my_lists.all(), shared_lists=shared_lists.all(), favorit_lists=favorit_lists.all(), select=id)
    else:
        return render_template('shopping/detail.html', my_lists=my_lists.all(), shared_lists=shared_lists.all(), favorit_lists=favorit_lists.all())


@blueprint.route('/get_detail', methods=['POST'])
@login_required
def get_detail():
    try:
        id = request.form['id']
    except BadRequestKeyError:
        return 'Error. Id not found'
    shopping_list = Shopping_list.query.filter_by(id=id).first()
    if shopping_list.check_access(current_user.id) < 2:
        return 'Error. Access is denied'
    shopping_items = Shopping_item.query.filter_by(list_id=id).all()
    form = ClearList()
    html = render_template('shopping/get_detail.html', shopping_list=shopping_list,
                           shopping_items=shopping_items, form=form)
    return jsonify({'html': html})


@blueprint.route('/add_shopping_item', methods=['POST'])
@login_required
def add_shopping_item():
    try:
        name = request.form['name']
        id = request.form['id']
    except BadRequestKeyError:
        return 'Error. Id or name not found'
    if name and id:
        item = Catalog.query.filter_by(name=name).first()
        shopping_list = Shopping_list.query.filter_by(id=id).first()
        if item and shopping_list and shopping_list.check_access(current_user.id) > 2:
            shopping_item = Shopping_item.query.filter_by(catalog_id=item.id, list_id=id).first()
            if shopping_item:
                shopping_item.quantity += 1
            else:
                shopping_item = Shopping_item(catalog_id=item.id, list_id=id, quantity=1)
                db.session.add(shopping_item)
            db.session.commit()
        else:
            return 'Error. Access is denied'
    return 'OK'


@blueprint.route('/clear_shopping_list', methods=['POST'])
@login_required
def clear_shopping_list():
    try:
        id = request.form['id']
    except BadRequestKeyError:
        return 'Error. Id not found'
    shopping_list = Shopping_list.query.filter_by(id=id).first()
    if shopping_list and shopping_list.check_access(current_user.id) > 2:
        try:
            Shopping_item.query.filter_by(list_id=id).delete()
            db.session.commit()
        except:
            db.session.rollback()
    else:
        return 'Error. Access is denied'
    return redirect(url_for('shopping.detail'), code=307)


@blueprint.route('/shopping_item_edit/', defaults={'id': 0})
@blueprint.route('/shopping_item_edit/<int:id>')
@admin_required
def shopping_item_edit(id):
    pass


@blueprint.route('/shopping_item_delete/<int:id>')
@admin_required
def shopping_item_delete(id):
    pass
