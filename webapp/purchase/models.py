from datetime import datetime
import os

from flask import current_app
from sqlalchemy.orm import relationship

from webapp.db import db


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inn = db.Column(db.String(20), index=True, unique=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.String(255))
    cash_desks = relationship('Cash_desk', backref='shop', lazy='dynamic')

    def __repr__(self):
        return '<Shop {}>'.format(self.name)


class Cash_desk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    fn = db.Column(db.String(16), unique=True, index=True)

    def __repr__(self):
        return '<Cash desk {} ({})>'.format(self.fn, self.shop.query.first())


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fp = db.Column(db.String(10), unique=True, index=True)
    date = db.Column(db.DateTime)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop = relationship('Shop')
    total = db.Column(db.Float)
    items = relationship('Purchase_Item', backref='purchase', lazy='dynamic')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = relationship("User", backref='purchases')

    def __repr__(self):
        return '<{} - {}({})>'.format(self.shop.name, self.total, self.date)


class Purchase_Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False)
    price_id = db.Column(db.Integer, db.ForeignKey('price.id'), nullable=False)
    price = relationship('Price')
    quantity = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float)

    def __repr__(self):
        return '<{}: {} * {} = {}>'.format(self.price.product.name, self.price.price, self.quantity, self.total)


class Process_Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = relationship('User', backref='processes')
    fn = db.Column(db.String(16), nullable=False)
    fp = db.Column(db.String(10), unique=True, index=True, nullable=False)
    fd = db.Column(db.String(10), nullable=False)
    fdate = db.Column(db.String(16), nullable=False)
    fsum = db.Column(db.String(10), nullable=False)
    max_attempts = db.Column(db.Integer, default=10, nullable=False)
    attempt = db.Column(db.Integer, default=0, nullable=False)

    @property
    def link(self):
        return os.path.abspath(os.path.join(current_app.config['TEMP_DIR'], '{}.json'.format(self.fp)))

    def status(self):
        if self.attempt == 0:
            return 'Проверка чека'
        if self.attempt == 1:
            return 'Получение подробной информации о чеке'
        if self.attempt == -1:
            return 'ok'
        if self.attempt == self.max_attempts:
            return 'error'
        return "Попытка {} получить подробную информацию".format(self.attempt)
