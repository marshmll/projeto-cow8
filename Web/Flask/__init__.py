from flask import Flask
from flask_login import LoginManager
from database.database import Base, engine, SessionLocal
from database.models import Usuario
import bcrypt
from base64 import b64encode

Base.metadata.create_all(bind=engine)

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'a318704cff8cefa6b49509810c54e4424483201bf340eb6be53deedff42e2668'

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "É necessário fazer login para acessar esta página."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return SessionLocal.query(Usuario).filter_by(id=user_id).first()

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for api parts of app
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    # create admin
    if not SessionLocal.query(Usuario).filter_by(username='admin').first():
        
        senha = b"Administrador@2025" # temp

        salt = bcrypt.gensalt(rounds=30, prefix=b'2a')
        salt_str = b64encode(salt).decode('utf-8')
        key = bcrypt.kdf(password=senha, salt=salt, desired_key_bytes=32, rounds=200)
        key_str = b64encode(key).decode(encoding='utf-8')

        usuario = Usuario(username="admin", nome_completo='Administrador', privilegios='Administrador', salt=salt_str, key=key_str)

        SessionLocal.add(usuario)
        SessionLocal.commit()
        SessionLocal.flush()

    # create regular user
    if not SessionLocal.query(Usuario).filter_by(username='renan').first():
        
        senha = b"Usuario@2025" # temp

        salt = bcrypt.gensalt(rounds=30, prefix=b'2a')
        salt_str = b64encode(salt).decode('utf-8')
        key = bcrypt.kdf(password=senha, salt=salt, desired_key_bytes=32, rounds=200)
        key_str = b64encode(key).decode(encoding='utf-8')

        usuario = Usuario(username="renan", nome_completo='Renan da Silva Oliveira Andrade', email="renandasilvaoliveiraandrade@gmail.com", privilegios='Usuário', salt=salt_str, key=key_str)

        SessionLocal.add(usuario)
        SessionLocal.commit()
        SessionLocal.flush()

    return app