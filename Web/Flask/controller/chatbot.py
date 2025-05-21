from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import login_required

from utils.routes import get_data
from utils.roles_required import operator_required

_chatbot = Blueprint('_chatbot', __name__)

@_chatbot.route('/chatbot')
@login_required
@operator_required
def chat_chatbot():
    data = get_data()
    data['routes']['Analista de Dados IA']['active'] = True
    
    return render_template('chatbot.html', data=data)

@_chatbot.route('/api/chatbot/prompt/', methods=['POST'])
@login_required
@operator_required
def prompt_chatbot():
    data = request.get_json()

    if 'content' not in data:
        return jsonify({'message': 'Invalid Payload.'}), 422

    response = current_app.extensions['ai'].prompt(data['content']).text()

    return jsonify({'response': response})