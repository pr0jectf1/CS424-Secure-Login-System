import os
import string
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '123abc'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pass1234@localhost/cs424'

    # come back and add environment variables
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
    
    mail.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)

    

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Post, Tag, Comment, Rating, Downvote

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(username):
        return User.query.get(str(username))

    return app


