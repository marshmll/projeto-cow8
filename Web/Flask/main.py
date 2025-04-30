from flask import Blueprint, render_template, abort, url_for
from flask_login import login_required, current_user
from database.database import get_db
from database import models
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

main = Blueprint('main', __name__)

links_admin = {
    'Geral': {
        'link': '/',
        'active': False
    },
    'Usuários': {
        'link': '/users/list',
        'active': False
    },
    'Balanças': {
        'link': '/scales/list',
        'active': False
    },
    'Analista de Dados IA': {
        'link': '/chatbot',
        'active': False
    }
}

links_user = {
    'Geral': {
        'link': '/',
        'active': False
    },
    'Balanças': {
        'link': '/scales/list',
        'active': False
    },
    'Analista de Dados IA': {
        'link': '/chatbot',
        'active': False
    }
}

def prepare_data():
    db = get_db()
    
    data = {}
    data['animal_count'] = len(db.query(models.Animal).all())
    data['measurement_count'] = len(db.query(models.ControlePesagem).all())
    data['user'] = current_user

    for key, value in links_user.items():
        value['active'] = False

    for key,value in links_admin.items():
        value['active'] = False

    if current_user.privilegios == 'Administrador':
        data['links'] = links_admin
    else:
        data['links'] = links_user

    db.remove()
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
    if current_user.privilegios != 'Administrador':
        abort(401, description='Acesso restrito.')

    data = prepare_data()
    data['links']['Usuários']['active'] = True

    return render_template('users_list.html', data=data)

@main.route('/users/register')
@login_required
def register_user():
    if current_user.privilegios != 'Administrador':
        abort(401, description='Acesso restrito.')

    data = prepare_data()
    data['links']['Usuários']['active'] = True

    return render_template('user_register.html', data=data)

@main.route('/scales/list')
@login_required
def list_scales():
    data = prepare_data()
    data['links']['Balanças']['active'] = True

    return render_template('scales_list.html', data=data)


@main.route('/scales/register')
@login_required
def register_scale():
    if current_user.privilegios != 'Administrador':
        abort(401, description='Acesso restrito.')

    data = prepare_data()
    data['links']['Balanças']['active'] = True

    return render_template('scale_register.html', data=data)


@main.route('/chatbot')
@login_required
def chat_chatbot():
    data = prepare_data()
    data['links']['Analista de Dados IA']['active'] = True
    
    return render_template('chatbot.html', data=data)