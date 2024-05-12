import os
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from .. import db

auth = Blueprint('auth', __name__,
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='assets'
                 )

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # TODO (validation, password hashing, error handling)

        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('auth.signup'))
        
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=int(os.getenv('SALTING_ROUNDS'))) # Secure hashing algorithm with salt
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Input validation: Check for empty fields 
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()
        # ... (check password, login user, error handling)
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.homepage'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))