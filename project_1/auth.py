from datetime import datetime
from unicodedata import category
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        regex = re.compile('[_!#$%^&*()<>?/\|\'\"}{~:]')

        if (regex.search(password) != None) or (regex.search(email) != None):
            flash('Cannot use restricted characters.', category='error')
            return redirect(url_for('auth.login'))


        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                user.login_count += 1
                date = datetime.now()
                user.last_login_date = date
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        regex = re.compile('[@_!#$%^&*()<>?/\|\'\"}{~:]')

        user = User.query.filter_by(email=email).first()
        
        if  (User.query.filter_by(username= username).first()):
            flash('Username is already taken', category='error')
        elif (User.query.filter_by(email= email).first()):
            flash('Email is already taken', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters. ', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character. ', category='error')
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character. ', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match. ', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters. ', category='error')
        elif (regex.search(password1) != None):
            flash('You cannot use restricted characters.', category='error')
        else:
            new_user = User(username=username, email=email, first_name=first_name, last_name=lastName, password=generate_password_hash(password1, method='sha256'), login_count=1)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created! ', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)



