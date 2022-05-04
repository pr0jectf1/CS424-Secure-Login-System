from datetime import timezone
from email.policy import default
from enum import unique
from operator import truediv
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from main import app

class User(db.Model, UserMixin):
    username = db.Column(db.String, primary_key=True, unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    login_count = db.Column(db.Integer, nullable=False)
    last_login_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    ratings = db.relationship('Rating', backref='user', passive_deletes=True)
    downvotes = db.relationship('Downvote', backref='user', passive_deletes=True)

    # Generate a timed token for username/password reset
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'username': self.username}).decode('utf-8')

    # verify that the token has not expired and as still valid
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            username = s.loads(token)['username']
        except:
            return None
        return User.query.get(username)

    def get_id(self):
        return (self.username)
    

class Post(db.Model):
    PostID = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String, db.ForeignKey('user.username', ondelete="CASCADE"), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    tags = db.relationship('Tag', backref='post', passive_deletes=True)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    ratings = db.relationship('Rating', backref='post', passive_deletes=True)
    downvotes = db.relationship('Downvote', backref='post', passive_deletes=True)
    

class Tag(db.Model):
    TagID = db.Column(db.Integer, primary_key=True, nullable=False)
    tag = db.Column(db.String(255))
    PostID = db.Column(db.Integer, db.ForeignKey('post.PostID', ondelete='CASCADE'), nullable=False)
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.String, db.ForeignKey('user.username', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.PostID', ondelete='CASCADE'), nullable=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.String, db.ForeignKey('user.username', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.PostID', ondelete='CASCADE'), nullable=False)
    vote = db.Column(db.String)

class Downvote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.String, db.ForeignKey('user.username', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.PostID', ondelete='CASCADE'), nullable=False)
    vote = db.Column(db.String)