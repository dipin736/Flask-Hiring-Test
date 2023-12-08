# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True) 
    name = db.Column(db.String(255)) 

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True) 
    name = db.Column(db.String(255)) 


class ProductMovement(db.Model):
    movement_id = db.Column(db.String(50), primary_key=True) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(255), nullable=True) 
    to_location = db.Column(db.String(255), nullable=True) 
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False) 
    qty = db.Column(db.Integer)
