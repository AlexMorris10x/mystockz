from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from .extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(100))
    cash = db.Column(db.Integer, default=10000)

    @property
    def unhashed_password(self):
        raise AttributeError("Cannot view unhashed password!")

    @unhashed_password.setter
    def unhashed_password(self, unhashed_password):
        self.password = generate_password_hash(unhashed_password)


class Stocks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    share = db.Column(db.Text)
    shares = db.Column(db.Integer)
    price = db.Column(db.Integer)
    time = db.Column(db.Text)
