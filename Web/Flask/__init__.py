import logging
from flask import Flask
from flask_login import LoginManager
from database.database import Base, engine, get_db
from database.models import Usuario
from database.callbacks import record_measurement, scale_status_refresh
import bcrypt
from .mqtt import MQTTClient
from base64 import b64encode
import os

# Initialize DB schema
Base.metadata.create_all(bind=engine)

def configure_login_manager(app):
    """Configure Flask-Login manager."""
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "É necessário fazer login para acessar esta página."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        db = get_db()
        try:
            return db.query(Usuario).filter_by(id=user_id).first()
        finally:
            db.remove()

def register_blueprints(app):
    """Register all application blueprints."""
    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint
    from .api import api as api_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)

def create_user(username, name, password, email=None, pfp_url=None, privileges='Usuário'):
    """Helper to create a new user securely."""
    salt = bcrypt.gensalt(rounds=12)
    salt_str = b64encode(salt).decode('utf-8')
    key = bcrypt.kdf(password=password.encode(), salt=salt, desired_key_bytes=32, rounds=100)
    key_str = b64encode(key).decode('utf-8')

    return Usuario(
        username=username,
        nome_completo=name,
        email=email,
        pfp_url=pfp_url,
        privilegios=privileges,
        salt=salt_str,
        key=key_str
    )

def initialize_admin_user():
    """Ensure admin user exists."""
    db = get_db()
    try:
        if not db.query(Usuario).filter_by(username='admin').first():
            admin = create_user(
                username='admin',
                name='Administrador',
                password='Administrador@2025',
                privileges='Administrador'
            )
            db.add(admin)
            db.commit()
    except Exception as e:
        logging.error(f"Failed to create admin user: {e}")
    finally:
        db.remove()

def initialize_regular_users():
    """Ensure regular users exist."""
    users = [
        {
            'username': 'renan',
            'pfp': 'https://github.com/marshmll.png',
            'name': 'Renan da Silva Oliveira Andrade',
            'email': 'renan.silva3@pucpr.edu.br'
        },
        {
            'username': 'ricardo',
            'pfp': 'https://github.com/Ricardo-LK.png',
            'name': 'Ricardo Lucas Kucek',
            'email': 'ricardo.kucek@pucpr.edu.br'
        },
        {
            'username': 'pedro',
            'pfp': 'https://github.com/prussianmaster1871.png',
            'name': 'Pedro Senes Velloso Ribeiro',
            'email': 'pedro.senes@pucpr.edu.br'
        },
        {
            'username': 'neto',
            'pfp': 'https://github.com/Vareja0.png',
            'name': 'Riscala Miguel Fadel Neto',
            'email': 'riscala.neto@pucpr.edu.br'
        },
        {
            'username': 'victor',
            'pfp': 'https://github.com/VictorFadel06.png',
            'name': 'Victor Valerio Fadel',
            'email': 'victor.fadel@pucpr.edu.br'
        },
    ]

    db = get_db()
    try:
        for user in users:
            if not db.query(Usuario).filter_by(username=user['username']).first():
                new_user = create_user(
                    username=user['username'],
                    name=user['name'],
                    password='Usuario@2025',
                    email=user['email'],
                    pfp_url=user['pfp']
                )
                db.add(new_user)
        db.commit()
    except Exception as e:
        logging.error(f"Failed to create regular users: {e}")
    finally:
        db.remove()
    

def create_app():
    """Flask application factory."""
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = 'a318704cff8cefa6b49509810c54e4424483201bf340eb6be53deedff42e2668'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.logger.setLevel(logging.INFO)

    # Setup components
    configure_login_manager(app)
    register_blueprints(app)
    initialize_admin_user()
    initialize_regular_users()

    # Only run MQTT client in the main reloader process
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        mqtt_client = MQTTClient()
        app.extensions['mqtt'] = mqtt_client

        if not mqtt_client.connect():
            app.logger.error("Failed to connect to MQTT")

        mqtt_client.add_listener_on_topic('database_handler', 'cow8/measurements', record_measurement)
        mqtt_client.add_listener_on_topic('scale_status_handler', 'cow8/status', scale_status_refresh)

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     pass

    return app
