from sqlalchemy.exc import IntegrityError
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from model.usuario import Usuario
from model.role import Role

from utils.routes import get_data
from utils.roles_required import admin_required, operator_required

_user = Blueprint('_user', __name__)

@_user.route('/users/list')
@login_required
@admin_required
def list_users():
    data = get_data()
    data['routes']['Usuários']['active'] = True

    return render_template('users_list.html', data=data)

@_user.route('/users/register')
@login_required
@admin_required
def register_user():
    data = get_data()
    data['routes']['Usuários']['active'] = True

    return render_template('user_register.html', data=data)

@_user.route('/api/users/all')
@login_required
@admin_required
def get_users():
    return jsonify([(user.as_dict(), role.as_dict()) for user, role in Usuario.get_all_usuarios()])

@_user.route('/api/users/<username>')
@login_required
@admin_required
def get_user(username: str):
    return jsonify(Usuario.get_usuario_by_username(username=username).as_dict())

@_user.route('/api/users/me')
@login_required
@operator_required
def get_me():
    return jsonify(current_user.as_dict())

@_user.route('/api/users/update/<username>', methods=['POST'])
@login_required
@admin_required
def update_user(username: str):
    data = request.get_json()

    user = Usuario.get_usuario_by_username(username=username)

    if not user:
        return jsonify('O usuário não existe no banco de dados.'), 404

    # Check for username conflict (if changing username)
    if 'username' in data and data['username'] != username:
        existing_user = Usuario.get_usuario_by_username(username=data['username'])
        if existing_user:
            return jsonify('Este username já está em uso.'), 409

    # Check for email conflict (if changing email)
    if 'email' in data and data['email'] != user.email:
        if data['email'] is not None:  # Only check if email is being set
            existing = Usuario.get_usuario_by_email(email=data['email'])
            if existing:
                return jsonify('Este email já está em uso'), 409

    try:
        user.update(data)
        return jsonify(user.as_dict())
    except IntegrityError as e:
        return jsonify({'error': 'Conflito de dados únicos (username/email já existe)'}), 409
    

@_user.route('/api/users/ban/<username>')
@login_required
@admin_required
def ban_user(username: str):
    user = Usuario.ban_user_by_username(username)

    if not user:
        abort(404, description='O usuário nao existe no banco de dados.')

    return jsonify(user.as_dict())

@_user.route('/api/users/delete/<username>')
@login_required
@admin_required
def del_user(username: str):
    return jsonify(Usuario.delete_user_by_username(username))

@_user.route('/api/users/register/', methods=['POST'])
@login_required
@admin_required
def create_user():
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    user = Usuario.get_usuario_by_username(username=username)

    if user:
        flash('Este nome de usuário já está em uso.')
        return redirect(url_for('_user.register_user'))
    
    user = Usuario.get_usuario_by_email(email=email)

    if user:
        flash('Este email já está em uso.')
        return redirect(url_for('_user.register_user'))

    try:
        Usuario.create_user(username, fullname, email, password, role=Role.get_role_by_name(name='Operador'))
    except IntegrityError as e:
        flash("Ocorreu um erro ao tentar criar o usuário: " + e)
        return redirect(url_for('_user.register_user'))
    
    return redirect(url_for('_user.list_users'))
