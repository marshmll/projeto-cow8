import logging
from flask import Flask
import os
from dotenv import load_dotenv

from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager

from controller.auth import auth as auth_blueprint
from controller.main import main as main_blueprint
from controller.api import api as api_blueprint
from controller.callbacks import Callbacks

from model.database import Base, engine
from model.usuario import Usuario

from utils.mqtt import MQTTClient
from utils.database_ai_assistant import DatabaseAIAssistant

# Initialize DB schema
Base.metadata.create_all(bind=engine)

# Load dotenv
load_dotenv()

def configure_login_manager(app: Flask):
    """Configure Flask-Login manager."""
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'É necessário fazer login para acessar esta página.'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.get_usuario_by_id(user_id)
        

def register_blueprints(app: Flask):
    """Register all application blueprints."""

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)


def initialize_admin_user():
    """Ensure admin user exists."""
    try:
        if not Usuario.get_usuario_by_username('admin'):
            admin = Usuario.create_user(
                username='admin',
                nome_completo='Administrador',
                email="admin@admin.com",
                password='Administrador@2025',
                privilegios='Administrador'
            )
    except IntegrityError as e:
        logging.error(f'Failed to create admin user: {e}')

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

    try:
        for user in users:
            if not Usuario.get_usuario_by_username(user['username']):
                Usuario.create_user(
                    username=user['username'],
                    nome_completo=user['name'],
                    password='Usuario@2025',
                    email=user['email'],
                    pfp_url=user['pfp']
                )
    except IntegrityError as e:
        logging.error(f'Failed to create regular users: {e}')

def create_app():
    """Flask application factory."""
    app = Flask(__name__, template_folder="view", static_folder='static')
    app.config['SECRET_KEY'] = 'a318704cff8cefa6b49509810c54e4424483201bf340eb6be53deedff42e2668'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.logger.setLevel(logging.DEBUG)

    # Setup components
    configure_login_manager(app)
    register_blueprints(app)
    initialize_admin_user()
    initialize_regular_users()

    # Only run in the main reloader process
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        mqtt_client = MQTTClient()
        app.extensions['mqtt'] = mqtt_client

        if not mqtt_client.connect():
            app.logger.error('Failed to connect to MQTT')

        if not mqtt_client.add_listener_on_topic('database_handler', 'cow8/measurements', Callbacks.record_measurement):
            app.logger.error('Failed to connect to cow8/measurements')
        
        if not mqtt_client.add_listener_on_topic('scale_status_handler', 'cow8/status', Callbacks.scale_status_refresh):
            app.logger.error('Failed to connect to cow8/status')


        if not os.getenv('OPENROUTER_API_KEY'):
            app.logger.error('Failed to load OpenRouter API key.')

        app.extensions['ai'] = DatabaseAIAssistant()

    return app
