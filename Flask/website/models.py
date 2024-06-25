from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    bikes = db.relationship('Bike', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    needs_maintenance = db.Column(db.Boolean, nullable=False)
    out_of_commission = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_entered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Bike {self.number} - {self.type}>'
