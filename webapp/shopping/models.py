from datetime import datetime

from webapp.db import db
from webapp.catalog.models import Catalog
from webapp.user.models import User


class Shopping_list(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    favorit = db.Column(db.Boolean, default=False, nullable=False)
    private = db.Column(db.Boolean, default=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship("User")
    items = db.relationship('Shopping_item', lazy='dynamic')
    access = db.relationship('List_access')
    date_create = db.Column(db.DateTime, default=datetime.utcnow)
    date_change = db.Column(db.DateTime, default=datetime.utcnow)

    def check_access(self, user_id):
        if self.author_id == user_id:
            return 4
        elif self.private:
            return 0
        else:
            level = self.access.filter_by(user_id=user_id).first()
            if level:
                return level.role
        return 0

    def access_dict(self):
        access_dict = {}
        for access in self.access:
            access_dict[access.user.username] = access.role
        return access_dict

    def __repr__(self):
        return '<Shopping list {}>'.format(self.name)


class Shopping_item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))
    catalog = db.relationship("Catalog")
    quantity = db.Column(db.Integer)
    list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'))

    @property
    def name(self):
        return self.catalog.name

    def __repr__(self):
        return '<{} - {}>'.format(self.name, self.quantity)


class List_access(db.Model):
    list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role = db.Column(db.Integer)
    user = db.relationship('User')
