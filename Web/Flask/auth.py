from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from database.database import SessionLocal
from database.models import Usuario
from base64 import b64decode
import bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    else:
        return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('user')
    password = request.form.get('pass')
    remember = True if request.form.get('remember') else False

    user = SessionLocal.query(Usuario).filter_by(username=username).first()

    if not user:
        flash('Usuário inexistente.')
        return redirect(url_for('auth.login'))

    salt = b64decode(user.salt)
    key = bcrypt.kdf(password=bytes(password, 'utf-8'), salt=salt, desired_key_bytes=32, rounds=200)
    expected = b64decode(user.key)

    if key != expected:
        flash('Credenciais inválidas.')
        return redirect(url_for('auth.login'))
    
    login_user(user, remember=remember)

    return redirect(url_for('main.index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))