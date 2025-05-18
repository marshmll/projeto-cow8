from datetime import datetime
import json

from sqlalchemy.exc import IntegrityError
from flask import Blueprint, abort, current_app, flash, jsonify, redirect, request, url_for
from flask_login import current_user, login_required

from model.api.means import Means
from model.api.health_metrics import HealthMetrics
from model.api.health_status import HealthStatus
from model.api.periodic_analisys import PeriodicAnalisys

from model.usuario import Usuario
from model.balanca import Balanca

api = Blueprint('api', __name__)

@api.route('/api/means')
@login_required
def get_means():
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    return jsonify(Means.get_means())
    
@api.route('/api/health_metrics')
@login_required
def get_health_metrics():
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    return jsonify(HealthMetrics.get_health_metrics())


@api.route('/api/health_status')
@login_required
def get_health_status():
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    return jsonify(HealthStatus.get_health_status())


@api.route('/api/periodic_analysis', methods=['POST'])
@login_required
def periodic_analysis():
    if current_user.status == 'Banido':
        return jsonify({'error': 'Usuário banido'}), 403

    data = request.get_json()
    try:
        # Parse dates and include the full end date by setting time to 23:59:59
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        end_datetime = datetime.combine(end_date, datetime.max.time())
    except (KeyError, ValueError):
        return jsonify({'error': 'Datas inválidas. Use o formato YYYY-MM-DD'}), 400

    if start_date > end_date:
        return jsonify({'error': 'Data inicial maior que data final'}), 400

    return jsonify(PeriodicAnalisys.get_periodic_analisys(start_datetime, end_datetime))

@api.route('/api/users/all')
@login_required
def get_users():
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    return jsonify([user.as_dict() for user in Usuario.get_all_usuarios()])

@api.route('/api/users/<username>')
@login_required
def get_user(username: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    return jsonify(Usuario.get_usuario_by_username(username=username).as_dict())

@api.route('/api/users/me')
@login_required
def get_me():
    return jsonify(current_user.as_dict())

@api.route('/api/users/update/<username>', methods=['POST'])
def update_user(username: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

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
    

@api.route('/api/users/ban/<username>')
def ban_user(username: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    user = Usuario.ban_user_by_username(username)

    if not user:
        abort(404, description='O usuário nao existe no banco de dados.')

    return jsonify(user.as_dict())

@api.route('/api/users/delete/<username>')
@login_required
def del_user(username: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    return jsonify(Usuario.delete_user_by_username(username))

@api.route('/api/users/register/', methods=['POST'])
@login_required
def register_user():
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    fullname = request.form.get('fullname')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    user = Usuario.get_usuario_by_username(username=username)

    if user:
        flash('Este nome de usuário já está em uso.')
        return redirect(url_for('main.register_user'))
    
    user = Usuario.get_usuario_by_email(email=email)

    if user:
        flash('Este email já está em uso.')
        return redirect(url_for('main.register_user'))

    try:
        Usuario.create_user(username, fullname, email, password)
    except IntegrityError as e:
        flash("Ocorreu um erro ao tentar criar o usuário: " + e)
        return redirect(url_for('main.register_user'))
    
    return redirect(url_for('main.list_users'))

@api.route('/api/scales/all')
@login_required
def get_scales():
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    return jsonify([scale.as_dict() for scale in Balanca.get_all_balancas()])

@api.route('/api/scales/<uid>')
@login_required
def get_scale(uid: str):
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))
    
    scale = Balanca.get_balanca_by_uid(uid)

    if not scale:
        abort(404, message='A balança solicitada não existe.')

    return jsonify(scale.as_dict())

@api.route('/api/scales/register/', methods=['POST'])
@login_required
def register_scale():
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    uid = request.form.get('uid')
    obs = request.form.get('obs')

    if uid:
        uid = uid.lower()

    scale = Balanca.get_balanca_by_uid(uid)

    if scale:
        flash('Este identificador único já foi usado por outra balança')
        return redirect(url_for('main.register_scale'))

    Balanca.create_balanca(uid, 'Offline', obs)
    
    return redirect(url_for('main.list_scales'))

@api.route('/api/scales/delete/<uid>', methods=['DELETE'])
@login_required
def del_scale(uid: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    return jsonify(Balanca.delete_balanca_by_uid(uid))

@api.route('/api/scales/<uid>/command/<command>')
@login_required
def scale_command(uid, command):
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    data = {
        'uid': uid,
        'command': command
    }

    if command == 'TARE':
        Balanca.update_ultima_calibragem(uid)

    payload = json.dumps(data)

    current_app.extensions['mqtt'].publish('cow8/commands', payload)

    return jsonify(data)

@api.route('/api/chatbot/prompt/', methods=['POST'])
@login_required
def prompt_chatbot():
    data = request.get_json()

    if 'content' not in data:
        return jsonify({'message': 'Invalid Payload.'}), 422

    res, sql = current_app.extensions['ai'].ask_about_data(data['content'])

    return jsonify({'response': res, 'sql': sql})