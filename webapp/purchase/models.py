from datetime import datetime

from webapp.db import db
from webapp.catalog.models import Price, Shop


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship('Shop')
    total = db.Column(db.Float)
    items = db.relationship('Purchase_Item', backref='purchase', lazy='dynamic')

    def __repr__(self):
        return '<{} - {}({})>'.format(self.shop.name, self.total, self.date)


class Purchase_Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False)
    price_id = db.Column(db.Integer, db.ForeignKey('price.id'), nullable=False)
    price = db.relationship('Price')
    quantity = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float)

    def __repr__(self):
        return '<{}: {} * {} = {}>'.format(self.price.product.name, self.price.price, self.quantity, self.total)