from datetime import datetime
from flask_login import UserMixin
from . import db

photo_categories = db.Table(
    'photo_categories',
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    caption = db.Column(db.String(250), nullable=False)
    file = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(600), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    categories = db.relationship('Category', secondary=photo_categories, backref=db.backref('photos', lazy=True))
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'caption': self.caption,
            'file': self.file,
            'desc': self.description,
            'categories': [category.name for category in self.categories]  # Return categories as list
        }

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    photos = db.relationship('Photo', backref='user', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    photo = db.relationship('Photo', backref=db.backref('comments', lazy=True))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)