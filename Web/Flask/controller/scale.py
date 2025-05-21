import json

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from model.balanca import Balanca

from utils.routes import get_data
from utils.roles_required import admin_required, operator_required

_scale = Blueprint('_scale', __name__)

@_scale.route('/scales/list')
@login_required
@operator_required
def list_scales():
    data = get_data()
    data['routes']['Balanças']['active'] = True

    return render_template('scales_list.html', data=data)


@_scale.route('/scales/register')
@login_required
@admin_required
def register_scale():
    data = get_data()
    data['routes']['Balanças']['active'] = True

    return render_template('scale_register.html', data=data)

@_scale.route('/api/scales/all')
@login_required
@operator_required
def get_scales():
    return jsonify([scale.as_dict() for scale in Balanca.get_all_balancas()])

@_scale.route('/api/scales/<uid>')
@login_required
@operator_required
def get_scale(uid: str):
    scale = Balanca.get_balanca_by_uid(uid)

    if not scale:
        abort(404, message='A balança solicitada não existe.')

    return jsonify(scale.as_dict())

@_scale.route('/api/scales/register/', methods=['POST'])
@login_required
@admin_required
def create_scale():
    uid = request.form.get('uid')
    obs = request.form.get('obs')

    if uid:
        uid = uid.lower()

    scale = Balanca.get_balanca_by_uid(uid)

    if scale:
        flash('Este identificador único já foi usado por outra balança')
        return redirect(url_for('_scale.register_scale'))

    Balanca.create_balanca(uid, 'Offline', obs)
    
    return redirect(url_for('_scale.list_scales'))

@_scale.route('/api/scales/delete/<uid>', methods=['DELETE'])
@login_required
@admin_required
def del_scale(uid: str):
    return jsonify(Balanca.delete_balanca_by_uid(uid))

@_scale.route('/api/scales/<uid>/command/<command>')
@login_required
@operator_required
def scale_command(uid, command):
    data = {
        'uid': uid,
        'command': command
    }

    if command == 'TARE':
        Balanca.update_ultima_calibragem(uid)

    payload = json.dumps(data)

    current_app.extensions['mqtt'].publish('cow8/commands', payload)

    return jsonify(data)