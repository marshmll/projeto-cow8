import logging
from flask import Flask
import os
from dotenv import load_dotenv

from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager

from controller.auth import _auth as auth_blueprint
from controller.user import _user as user_blueprint
from controller.scale import _scale as scale_blueprint
from controller.statistics import _statistics as statistics_blueprint
from controller.chatbot import _chatbot as chatbot_blueprint
from controller.other import _other as other_blueprint

from controller.callbacks import Callbacks

from model.database import Base, engine
from model.usuario import Usuario
from model.role import Role

from utils.mqtt import MQTTClient
from utils.database_ai_assistant import DatabaseAIAssistant

# Load dotenv
load_dotenv()

def configure_login_manager(app: Flask):
    """Configure Flask-Login manager."""
    login_manager = LoginManager()
    login_manager.login_view = '_auth.login'
    login_manager.login_message = 'É necessário fazer login para acessar esta página.'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.get_usuario_by_id(user_id)
        

def register_blueprints(app: Flask):
    """Register all application blueprints."""
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(scale_blueprint)
    app.register_blueprint(statistics_blueprint)
    app.register_blueprint(chatbot_blueprint)
    app.register_blueprint(other_blueprint)


def initialize_roles():
    roles = ['Administrador', 'Operador']

    try:
        for name in roles:
            if not Role.get_role_by_name(name=name):
                Role.create_role(name=name)
    except IntegrityError as e:
        logging.error(f'Failed to create roles: {e}')

def initialize_admin_user():
    """Ensure admin user exists."""
    try:
        role = Role.get_role_by_name(name='Administrador')
        if not Usuario.get_usuario_by_username('admin'):
            Usuario.create_user(
                username='admin',
                nome_completo='Administrador',
                email="admin@admin.com",
                password='Administrador@2025',
                role=role
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
        role = Role.get_role_by_name(name='Operador')
        for user in users:
            if not Usuario.get_usuario_by_username(user['username']):
                Usuario.create_user(
                    username=user['username'],
                    nome_completo=user['name'],
                    password='Usuario@2025',
                    email=user['email'],
                    pfp_url=user['pfp'],
                    role=role
                )
    except IntegrityError as e:
        logging.error(f'Failed to create regular users: {e}')

def create_app():
    """Flask application factory."""
    app = Flask(__name__, template_folder="view", static_folder='static')
    app.config['SECRET_KEY'] = 'a318704cff8cefa6b49509810c54e4424483201bf340eb6be53deedff42e2668'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.logger.setLevel(logging.DEBUG)

    configure_login_manager(app)
    register_blueprints(app)

    # Only run in the main reloader process
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        # Initialize DB schema
        Base.metadata.create_all(bind=engine)

        # Setup components
        initialize_roles()
        initialize_admin_user()
        initialize_regular_users()

        mqtt_client = MQTTClient()
        app.extensions['mqtt'] = mqtt_client

        if not mqtt_client.connect(broker='broker.hivemq.com'):
            app.logger.error('Failed to connect to MQTT')

        if not mqtt_client.add_listener_on_topic('database_handler', 'cow8/measurements', Callbacks.record_measurement):
            app.logger.error('Failed to connect to cow8/measurements')
        
        if not mqtt_client.add_listener_on_topic('scale_status_handler', 'cow8/status', Callbacks.scale_status_refresh):
            app.logger.error('Failed to connect to cow8/status')


        if not os.getenv('OPENROUTER_API_KEY'):
            app.logger.error('Failed to load OpenRouter API key.')

        app.extensions['ai'] = DatabaseAIAssistant()

    return app
