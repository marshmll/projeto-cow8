from datetime import datetime
from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from model.statistics.health_metrics import HealthMetrics
from model.statistics.health_status import HealthStatus
from model.statistics.means import Means
from model.statistics.periodic_analisys import PeriodicAnalisys

from utils.routes import get_data
from utils.roles_required import operator_required

_statistics = Blueprint('_statistics', __name__)

@_statistics.route('/')
@login_required
@operator_required
def index(): 
    data = get_data()
    data['routes']['Geral']['active'] = True

    return render_template('index.html', data=data)

@_statistics.route('/api/means')
@login_required
@operator_required
def get_means():
    return jsonify(Means.get_means())
    
@_statistics.route('/api/health_metrics')
@login_required
@operator_required
def get_health_metrics():
    return jsonify(HealthMetrics.get_health_metrics())


@_statistics.route('/api/health_status')
@login_required
@operator_required
def get_health_status():
    return jsonify(HealthStatus.get_health_status())


@_statistics.route('/api/periodic_analysis', methods=['POST'])
@login_required
@operator_required
def periodic_analysis():
    data = request.get_json()
    try:
        # Parse dates and include the full end date by setting time to 23:59:59
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        end_datetime = datetime.combine(end_date, datetime.max.time())
    except (KeyError, ValueError):
        return jsonify({'error': 'Datas inválidas. Use o formato YYYY-MM-DD'}), 400

    if start_date > end_date:
        return jsonify({'error': 'Data inicial maior que data final'}), 400

    return jsonify(PeriodicAnalisys.get_periodic_analisys(start_datetime, end_datetime))