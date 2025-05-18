from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from model.animal import Animal
from model.registro_pesagem import RegistroPesagem

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
    data = {}
    data['animal_count'] = len(Animal.get_all_animais())
    data['measurement_count'] = len(RegistroPesagem.get_all_registros())
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