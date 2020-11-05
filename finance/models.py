from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from finance import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    hash = db.Column(db.String(120), nullable=False)
    cash = db.Column(db.Float, nullable=False, default=10000.)
    transactions = db.relationship('Transactions', backref='transactor', lazy=True)
    
    def __repr__(self):
        return f"User({self.username})"
    
class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    shares =  db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(), nullable=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow())
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"symbol({self.symbol}), shares({self.shares}), price({self.price})"
    