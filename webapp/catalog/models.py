from datetime import datetime

from webapp.db import db


class Catalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    level = db.Column(db.Integer)
    parent_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))
    children = db.relationship('Catalog', backref=db.backref('catalog', remote_side=[id]))
    products = db.relationship('Product', backref='catalog', lazy='dynamic')

    def __repr__(self):
        return '<Catalog {}>'.format(self.name)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'), nullable=False)

    def __repr__(self):
        return '<Product {}>'.format(self.name)


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self):
        return '<Shop {}>'.format(self.name)


class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product')
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship('Shop')
    discont = db.Column(db.Boolean, default=False, nullable=False)
    cost = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<{} - {}({}, {})>'.format(self.product.name, self.cost, self.date, self.shop.name)