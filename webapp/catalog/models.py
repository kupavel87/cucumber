from datetime import datetime

from webapp.db import db


class Catalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    level = db.Column(db.Integer)
    parent_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))
    children = db.relationship('Catalog', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    products = db.relationship('Product', backref='catalog', lazy='dynamic')

    def get_level(self):
        if self.level is None:
            if self.parent_id:
                self.level = self.parent.get_level() + 1
            else:
                self.level = 0
        return self.level

    def __repr__(self):
        return '<Catalog {}>'.format(self.name)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(13), index=True, unique=True)
    name = db.Column(db.String(255), index=True, unique=True, nullable=False)
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'), nullable=False)
    pen_names = db.relationship('Pen_name', backref='product', lazy='dynamic')

    def __repr__(self):
        return '<Product {}>'.format(self.name)


class Pen_name(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    name = db.Column(db.String(255), index=True, unique=True, nullable=False)

    def __repr__(self):
        return '<Pen name {}>'.format(self.name)


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inn = db.Column(db.String(20), index=True, unique=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.String(255))

    def __repr__(self):
        return '<Shop {}>'.format(self.name)


class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), index=True, nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), index=True, nullable=False)
    discount = db.Column(db.Boolean, default=False, nullable=False)
    price = db.Column(db.Float, default=0.0, nullable=False)

    product = db.relationship('Product')
    shop = db.relationship('Shop')

    def __repr__(self):
        if self.product_id and self.shop_id:
            return '<{} - {}({}, {})>'.format(self.product.name, self.price, self.date, self.shop.name)
        return 'Price: {}'.format(self.price)
