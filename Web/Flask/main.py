from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from database.database import SessionLocal
from database import models

main = Blueprint('main', __name__)

links_admin = {
    'Geral': {
        'link': '/',
        'active': False
    },
    'Relatórios': {
        'link': '/reports',
        'active': False
    },
    'Usuários': {
        'link': '/users/list',
        'active': False
    }
}

links_user = {
    'Geral': {
        'link': '/',
        'active': False
    },
    'Relatórios': {
        'link': '/reports',
        'active': False
    },
}

def prepare_data():
    data = {}
    data['animal_count'] = len(SessionLocal.query(models.Animal).all())
    data['measurement_count'] = len(SessionLocal.query(models.ControlePesagem).all())
    data['user'] = current_user

    for key, value in links_user.items():
        value['active'] = False

    for key,value in links_admin.items():
        value['active'] = False

    if current_user.privilegios == 'Administrador':
        data['links'] = links_admin
    else:
        data['links'] = links_user

    return data

@main.route('/')
@login_required
def index(): 
    data = prepare_data()
    data['links']['Geral']['active'] = True
    return render_template('index.html', data=data)

@main.route('/reports')
@login_required
def reports():
    data = prepare_data()

    return render_template('reports.html', data=data)

@main.route('/users/list')
@login_required
def list_users():
    if current_user.privilegios != "Administrador":
        abort(401, description="Acesso restrito.")

    data = prepare_data()
    data['links']['Usuários']['active'] = True

    return render_template('users_list.html', data=data)


