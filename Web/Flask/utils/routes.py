from flask_login import current_user

routes_admin = {
    'Geral': {
        'route': '/',
        'active': False
    },
    'Usuários': {
        'route': '/users/list',
        'active': False
    },
    'Balanças': {
        'route': '/scales/list',
        'active': False
    },
    'Analista de Dados IA': {
        'route': '/chatbot',
        'active': False
    }
}

routes_user = {
    'Geral': {
        'route': '/',
        'active': False
    },
    'Balanças': {
        'route': '/scales/list',
        'active': False
    },
    'Analista de Dados IA': {
        'route': '/chatbot',
        'active': False
    }
}

def get_data():
    data = {}
    data['user'] = current_user

    for key, value in routes_user.items():
        value['active'] = False

    for key,value in routes_admin.items():
        value['active'] = False

    if current_user.role.name == 'Administrador':
        data['routes'] = routes_admin
    else:
        data['routes'] = routes_user

    return data
