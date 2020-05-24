from flask import Blueprint, flash, render_template, redirect, url_for, request, jsonify, json
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequestKeyError
from urllib.parse import unquote

from webapp.catalog.models import Catalog
from webapp.shopping.forms import CreateShoppingListForm
from webapp.shopping.models import Shopping_list, Shopping_item, List_access
from webapp.user.models import User
from webapp.db import db

blueprint = Blueprint('shopping', __name__, url_prefix='/shopping')


@blueprint.route('/')
@login_required
def index():
    title = 'Список покупок'
    form = CreateShoppingListForm()
    users = User.query.filter(User.id != current_user.get_id()).all()
    # shared_lists = List_access.query.filter_by(user_id=current_user.get_id()).lists.all()
    return render_template('shopping/index.html', page_title=title, form=form, users=users)


@blueprint.route('/update_grid')
@login_required
def update_grid():
    my_lists = Shopping_list.query.filter_by(author_id=current_user.get_id())
    shared_lists_id = [item.list_id for item in List_access.query.filter_by(user_id=current_user.get_id()).all()]
    shared_lists = Shopping_list.query.filter(Shopping_list.id.in_(shared_lists_id))
    favorit_lists = my_lists.union(shared_lists).filter_by(favorit=True)
    html = render_template('shopping/grid.html', my_lists=my_lists.all(), shared_lists=shared_lists.all(), favorit_lists=favorit_lists.all())
    return jsonify({'html': html})


@blueprint.route('/create_list', methods=['POST'])
@login_required
def create_list():
    data = request.get_json()
    try:
        new_list = Shopping_list(name=data['name'], favorit=data.get('favorit'), private=data.get('private'),
                                 author_id=current_user.get_id())
    except BadRequestKeyError:
        return jsonify({'result': 'Error'})
    db.session.add(new_list)
    if not new_list.private:
        access = data.get('access')
        access_users = User.query.filter(User.username.in_(access.keys())).all()
        for user in access_users:
            list_access = List_access(list_id=new_list.id, user_id=user.id, role=access.get(user.username, 0))
            db.session.add(list_access)
    db.session.commit()
    return jsonify({'result': 'OK'})


@blueprint.route('/property_list', methods=['POST'])
@login_required
def property_list():
    try:
        id = request.form['id']
    except BadRequestKeyError:
        return "Error"
    shopping_list = Shopping_list.query.filter_by(id=id).first()
    if not shopping_list:
        return "Error"
    answer = {'name': shopping_list.name, 'favorit': shopping_list.favorit, 'private': shopping_list.private}
    if not shopping_list.private:
        access_list = {}
        for access in shopping_list.access:
            access_list[access.user.username] = access.role
        answer['access'] = access_list
    return jsonify(answer)


@blueprint.route('/delete_list', methods=['POST'])
@login_required
def delete_list():
    try:
        id = request.form['id']
    except BadRequestKeyError:
        return 'Error. Id not found'
    shopping_list = Shopping_list.query.filter_by(id=id).first()
    if shopping_list and shopping_list.check_access(current_user.id) > 3:
        db.session.delete(shopping_list)
        db.session.commit()
        return 'OK. Shopping list deleted'
    return 'Error. Access is denied'


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
    html = render_template('shopping/get_detail.html', shopping_list=shopping_list, shopping_items=shopping_items)
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
    # else:
    #     try:
    #         Shopping_item.query.delete()
    #         db.session.commit()
    #     except:
    #         db.session.rollback()
    return 'OK'


# @blueprint.route('/update_shopping_list')
# def update_shopping_list():
#     shopping_list = Shopping_item.query.all()
#     html = render_template('purchase/update_shopping_list.html', shopping_list=shopping_list)
    # return jsonify({"html": html})


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
    return 'OK'