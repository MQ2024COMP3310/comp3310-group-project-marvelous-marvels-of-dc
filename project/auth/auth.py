# Importing necessary libraries and modules.
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from .. import db
from ..forms import LoginForm, RegisterForm

# Define a blueprint for authentication routes.
auth = Blueprint('auth', __name__, template_folder='templates')

# Route for user registration.
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Check if the username already exists.
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))

        # Hash the password before storing it.
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form)

# Route for user login.
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Fetch the user from the database.
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.homepage'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
    return render_template('auth/login.html', form=form)

# Route for user logout.
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.homepage'))