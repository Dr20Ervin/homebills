from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False) # Long string for hash
    role = db.Column(db.String(20), default='Viewer')
    theme = db.Column(db.String(10), default='light')

    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(10))
    icon = db.Column(db.String(50), default='mdi-file') 
    color = db.Column(db.String(20), default='#4e73df') 
    default_cost = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)

class BillEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category')
    cost = db.Column(db.Float, nullable=False)
    usage = db.Column(db.Float, nullable=True) 
    note = db.Column(db.String(200))

class AppSetting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(100))