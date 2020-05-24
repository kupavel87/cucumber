from datetime import datetime

from webapp.db import db
from webapp.catalog.models import Price


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    price_id = db.Column(db.Integer, db.ForeignKey('price.id'), nullable=False)
    price = db.relationship('Price')
    quantity = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<{} - {}({})>'.format(self.price.product.name, self.price.cost * self.quantity, self.quantity)
