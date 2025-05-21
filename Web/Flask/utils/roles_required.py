from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('_auth.login'))    
        elif current_user.role.name != "Administrador":
            abort(401, description='Acesso restrito.')
        return f(*args, **kwargs)
    return decorated_function


def operator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('_auth.login'))    
        elif current_user.role.name != "Operador" and current_user.role.name != "Administrador":
            abort(401, description='Acesso restrito.')
        elif current_user.status == 'Banido':
            flash('O usuário foi banido por tempo indeterminado.')
            return redirect(url_for('_auth.login'))

        return f(*args, **kwargs)
    return decorated_function