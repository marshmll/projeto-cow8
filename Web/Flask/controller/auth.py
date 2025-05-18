from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user

from model.usuario import Usuario
from utils.pbkdf import Pbkdf

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    else:
        return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    username_or_email = request.form.get('user')
    password = request.form.get('pass')
    remember = True if request.form.get('remember') else False

    user = Usuario.get_usuario_by_username_or_email(username_or_email)

    if not user:
        flash('Usuário inexistente.')
        return redirect(url_for('auth.login'))
    
    if user.status == "Banido":
        flash('Este usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    if not Pbkdf.is_valid_password(user.key, user.salt, password):
        flash('Credenciais inválidas.')
        return redirect(url_for('auth.login'))
    
    login_user(user, remember=remember)

    return redirect(url_for('main.index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))