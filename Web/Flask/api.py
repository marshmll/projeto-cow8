from flask import Blueprint, jsonify, abort, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from database.database import get_db
from database import models
from datetime import datetime, timedelta
from sqlalchemy import extract, func, distinct, update, case, exists
from sqlalchemy.exc import IntegrityError
import locale
import bcrypt
import json
from base64 import b64encode
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

api = Blueprint('api', __name__)

@api.route('/api/means')
@login_required
def get_means():
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    # Consulta para obter o peso médio por mês
    db = get_db()
    current_year = datetime.now().year
    monthly_avg = db.query(
        extract('month', models.ControlePesagem.datahora_pesagem).label('month'),
        func.avg(models.ControlePesagem.medicao_peso).label('avg_weight')
    ).filter(
        extract('year', models.ControlePesagem.datahora_pesagem) == current_year
    ).group_by(
        extract('month', models.ControlePesagem.datahora_pesagem)
    ).all()
    
    # Criar uma lista com todos os meses do ano (meses sem dados terão valor 0)
    monthly_data = []
    for month in range(1, 13):
        avg_weight = next((item.avg_weight for item in monthly_avg if item.month == month), None)
        monthly_data.append({
            'month': month,
            'month_name': datetime(current_year, month, 1).strftime('%B'),
            'avg_weight': float(avg_weight) if avg_weight is not None else 0
        })

    db.remove()
    return jsonify(monthly_data)
    
@api.route('/api/health_metrics')
@login_required
def get_health_metrics():
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    current_year = datetime.now().year
    db = get_db()
    
    try:
        # 1. Subquery para a última pesagem de cada animal em cada mês
        last_weight_subq = db.query(
            models.ControlePesagem.id_animal,
            extract('month', models.ControlePesagem.datahora_pesagem).label('month'),
            func.max(models.ControlePesagem.datahora_pesagem).label('last_date')
        ).filter(
            extract('year', models.ControlePesagem.datahora_pesagem) == current_year
        ).group_by(
            models.ControlePesagem.id_animal,
            extract('month', models.ControlePesagem.datahora_pesagem)
        ).subquery()

        # 2. Junta a última pesagem com o peso médio da raça
        last_weights = db.query(
            last_weight_subq.c.id_animal,
            last_weight_subq.c.month,
            models.ControlePesagem.medicao_peso,
            models.DadosAnimal.peso_medio
        ).join(
            models.ControlePesagem,
            (models.ControlePesagem.id_animal == last_weight_subq.c.id_animal) &
            (models.ControlePesagem.datahora_pesagem == last_weight_subq.c.last_date)
        ).join(
            models.Animal, models.Animal.id == models.ControlePesagem.id_animal
        ).join(
            models.DadosAnimal, models.DadosAnimal.id == models.Animal.id_dados_animal
        ).all()

        # Organiza animais abaixo do peso
        underweight_by_month = {}
        for lw in last_weights:
            medicao_peso = float(lw.medicao_peso) if lw.medicao_peso is not None else None
            peso_medio = float(lw.peso_medio) if lw.peso_medio is not None else None

            if peso_medio and medicao_peso and medicao_peso < peso_medio * 0.9:
                underweight_by_month.setdefault(int(lw.month), set()).add(lw.id_animal)

        # 3. Subquery para detectar perda de peso dentro do mês
        weight_change_subq = db.query(
            models.ControlePesagem.id_animal,
            extract('month', models.ControlePesagem.datahora_pesagem).label('month'),
            (models.ControlePesagem.medicao_peso - func.lag(models.ControlePesagem.medicao_peso).over(
                partition_by=[
                    models.ControlePesagem.id_animal,
                    extract('month', models.ControlePesagem.datahora_pesagem)
                ],
                order_by=models.ControlePesagem.datahora_pesagem
            )).label('weight_diff')
        ).filter(
            extract('year', models.ControlePesagem.datahora_pesagem) == current_year
        ).subquery()

        weight_loss_by_month = {}
        rows = db.query(weight_change_subq).filter(weight_change_subq.c.weight_diff < 0).all()

        for row in rows:
            weight_loss_by_month.setdefault(int(row.month), set()).add(row.id_animal)

        # 4. Combina sem duplicar
        health_metrics = []
        for month in range(1, 13):
            underweight_animals = underweight_by_month.get(month, set())
            weight_loss_animals = weight_loss_by_month.get(month, set())

            # Combina sem repetir animal
            total_at_risk_animals = underweight_animals.union(weight_loss_animals)

            health_metrics.append({
                'month': month,
                'month_name': datetime(current_year, month, 1).strftime('%B'),
                'underweight_count': len(underweight_animals),
                'weight_loss_count': len(weight_loss_animals),
                'total_at_risk': len(total_at_risk_animals)
            })

        return jsonify(health_metrics)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@api.route('/api/health_status')
@login_required
def get_health_status():
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    db = get_db()
    try:
        today = datetime.now()
        current_year = today.year
        current_month = today.month

        start_of_month = datetime(current_year, current_month, 1)
        if current_month == 12:
            start_of_next_month = datetime(current_year + 1, 1, 1)
        else:
            start_of_next_month = datetime(current_year, current_month + 1, 1)

        # Subquery: primeira pesagem do mês
        first_weights_subq = db.query(
            models.ControlePesagem.id_animal,
            func.min(models.ControlePesagem.datahora_pesagem).label('first_date')
        ).filter(
            models.ControlePesagem.datahora_pesagem >= start_of_month,
            models.ControlePesagem.datahora_pesagem < start_of_next_month
        ).group_by(
            models.ControlePesagem.id_animal
        ).subquery()

        # Subquery: última pesagem do mês
        last_weights_subq = db.query(
            models.ControlePesagem.id_animal,
            func.max(models.ControlePesagem.datahora_pesagem).label('last_date')
        ).filter(
            models.ControlePesagem.datahora_pesagem >= start_of_month,
            models.ControlePesagem.datahora_pesagem < start_of_next_month
        ).group_by(
            models.ControlePesagem.id_animal
        ).subquery()

        # Recuperar pesos associados
        first_weights = db.query(
            models.ControlePesagem.id_animal,
            models.ControlePesagem.medicao_peso,
            models.ControlePesagem.datahora_pesagem
        ).join(
            first_weights_subq,
            (models.ControlePesagem.id_animal == first_weights_subq.c.id_animal) &
            (models.ControlePesagem.datahora_pesagem == first_weights_subq.c.first_date)
        ).all()

        last_weights = db.query(
            models.ControlePesagem.id_animal,
            models.ControlePesagem.medicao_peso,
            models.ControlePesagem.datahora_pesagem
        ).join(
            last_weights_subq,
            (models.ControlePesagem.id_animal == last_weights_subq.c.id_animal) &
            (models.ControlePesagem.datahora_pesagem == last_weights_subq.c.last_date)
        ).all()

        first_map = {fw.id_animal: (float(fw.medicao_peso), fw.datahora_pesagem) for fw in first_weights}
        last_map = {lw.id_animal: (float(lw.medicao_peso), lw.datahora_pesagem) for lw in last_weights}

        # Pega dados dos animais
        animals_data = db.query(
            models.Animal.id,
            models.DadosAnimal.peso_medio
        ).join(
            models.DadosAnimal, models.Animal.id_dados_animal == models.DadosAnimal.id
        ).all()

        if not animals_data:
            return jsonify({'health_status': 100, 'message': 'Nenhum animal cadastrado'})

        healthy = warning = critical = no_data = 0

        for animal in animals_data:
            first_info = first_map.get(animal.id)
            last_info = last_map.get(animal.id)

            if not first_info or not last_info or animal.peso_medio is None:
                no_data += 1
                continue

            first_weight, first_date = first_info
            last_weight, last_date = last_info
            expected_final_weight = float(animal.peso_medio)

            # Cálculo de tempo real passado no mês
            days_in_month = (start_of_next_month - start_of_month).days
            days_passed = (last_date - first_date).days or 1  # evita zero

            expected_progress = expected_final_weight - first_weight
            expected_weight = first_weight + (expected_progress * (days_passed / days_in_month))

            weight_ratio = last_weight / expected_weight if expected_weight else 0

            # Tendência (ganho ou perda no mês)
            trend_percent = ((last_weight - first_weight) / first_weight) * 100 if first_weight else 0

            # Classificação mais refinada
            if weight_ratio >= 0.95 and trend_percent >= -1:
                healthy += 1
            elif weight_ratio >= 0.85 or (weight_ratio >= 0.9 and trend_percent >= -3):
                warning += 1
            else:
                critical += 1

        total_with_data = healthy + warning + critical

        health_score = (
            (healthy * 1.0 + warning * 0.6 + critical * 0.2) /
            max(1, total_with_data) * 100
        )

        return jsonify({
            'health_status': round(health_score, 2),
            'healthy_animals': healthy,
            'warning_animals': warning,
            'critical_animals': critical,
            'no_data_animals': no_data,
            'total_animals': healthy + warning + critical + no_data,
            'period': {
                'year': current_year,
                'month': current_month,
                'start_date': start_of_month.strftime('%Y-%m-%d'),
                'end_date': (start_of_next_month - timedelta(days=1)).strftime('%Y-%m-%d')
            },
            'metrics': {
                'calculation_date': today.isoformat(),
                'weight_ratio_thresholds': {
                    'healthy': '≥95%',
                    'warning': '85%-94%',
                    'critical': '<85%'
                },
                'trend_thresholds': {
                    'healthy': '≥-1%',
                    'warning': '-1% to -3%',
                    'critical': '<-3%'
                }
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()


@api.route('/api/periodic_analysis', methods=['POST'])
@login_required
def periodic_analysis():
    if current_user.status == 'Banido':
        return jsonify({'error': 'Usuário banido'}), 403

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

    db = get_db()

    try:
        # Weight statistics
        weight_query = db.query(
            func.avg(models.ControlePesagem.medicao_peso),
            func.min(models.ControlePesagem.medicao_peso),
            func.max(models.ControlePesagem.medicao_peso),
            func.count(models.ControlePesagem.datahora_pesagem)
        ).filter(
            models.ControlePesagem.datahora_pesagem >= start_datetime,
            models.ControlePesagem.datahora_pesagem <= end_datetime
        ).first()
        avg_weight, min_weight, max_weight, weight_count = weight_query or (0, 0, 0, 0)

        # Total animals and underweight count
        total_animals = db.query(func.count(models.Animal.id)).scalar() or 0
        underweight_count = db.query(
            func.count(distinct(models.ControlePesagem.id_animal))
        ).join(
            models.Animal, models.Animal.id == models.ControlePesagem.id_animal
        ).join(
            models.DadosAnimal, models.DadosAnimal.id == models.Animal.id_dados_animal
        ).filter(
            models.ControlePesagem.datahora_pesagem >= start_datetime,
            models.ControlePesagem.datahora_pesagem <= end_datetime,
            models.ControlePesagem.medicao_peso < models.DadosAnimal.peso_medio * 0.9
        ).scalar() or 0

       # Animal trend classification
        trend_subquery = db.query(
            models.Animal.id,
            case(
                # Gaining if ANY measurement is >105% of average
                (exists().where(
                    models.ControlePesagem.id_animal == models.Animal.id,
                    models.ControlePesagem.medicao_peso > models.DadosAnimal.peso_medio * 1.05,
                    models.ControlePesagem.datahora_pesagem >= start_datetime,
                    models.ControlePesagem.datahora_pesagem <= end_datetime
                ), 'gaining'),
                # Losing if ANY measurement is <95% of average AND NONE are >105%
                (exists().where(
                    models.ControlePesagem.id_animal == models.Animal.id,
                    models.ControlePesagem.medicao_peso < models.DadosAnimal.peso_medio * 0.95,
                    models.ControlePesagem.datahora_pesagem >= start_datetime,
                    models.ControlePesagem.datahora_pesagem <= end_datetime
                ) & ~exists().where(
                    models.ControlePesagem.id_animal == models.Animal.id,
                    models.ControlePesagem.medicao_peso > models.DadosAnimal.peso_medio * 1.05,
                    models.ControlePesagem.datahora_pesagem >= start_datetime,
                    models.ControlePesagem.datahora_pesagem <= end_datetime
                ), 'losing'),
                # Stable if ALL measurements are between 95%-105% of average
                else_='stable'
            ).label('trend')
        ).join(
            models.DadosAnimal, models.DadosAnimal.id == models.Animal.id_dados_animal
        ).filter(
            exists().where(
                models.ControlePesagem.id_animal == models.Animal.id,
                models.ControlePesagem.datahora_pesagem >= start_datetime,
                models.ControlePesagem.datahora_pesagem <= end_datetime
            )
        ).subquery()

        trend_counts = db.query(
            func.sum(case((trend_subquery.c.trend == 'gaining', 1), else_=0)).label('gaining_count'),
            func.sum(case((trend_subquery.c.trend == 'losing', 1), else_=0)).label('losing_count'),
            func.sum(case((trend_subquery.c.trend == 'stable', 1), else_=0)).label('stable_count')
        ).select_from(trend_subquery).first()

        # Breed distribution
        breed_distribution = db.query(
            models.DadosAnimal.raca,
            func.count(models.Animal.id)
        ).join(
            models.Animal, models.Animal.id_dados_animal == models.DadosAnimal.id
        ).group_by(models.DadosAnimal.raca).all()

        # Scale usage
        scale_usage = db.query(
            models.Balanca.uid,
            func.count(models.ControlePesagem.uid_balanca)
        ).join(
            models.ControlePesagem, models.ControlePesagem.uid_balanca == models.Balanca.uid
        ).filter(
            models.ControlePesagem.datahora_pesagem >= start_datetime,
            models.ControlePesagem.datahora_pesagem <= end_datetime
        ).group_by(models.Balanca.uid).all()

        return jsonify({
            'period': {
                'start': start_datetime.strftime('%Y-%m-%d'),
                'end': end_datetime.strftime('%Y-%m-%d'),
                'days': (end_datetime - start_datetime).days + 1
            },
            'animals': {
                'total': total_animals,
                'underweight': underweight_count,
                'underweight_percentage': round((underweight_count / total_animals * 100), 2) if total_animals else 0
            },
            'weight': {
                'average': float(avg_weight) if avg_weight else 0,
                'minimum': float(min_weight) if min_weight else 0,
                'maximum': float(max_weight) if max_weight else 0,
                'measurements': weight_count
            },
            'trends': {
                'gaining': trend_counts.gaining_count or 0,
                'losing': trend_counts.losing_count or 0,
                'stable': trend_counts.stable_count or 0
            },
            'breeds': [
                {'name': breed, 'count': count} for breed, count in breed_distribution
            ],
            'scales': [
                {'uid': uid, 'usage': usage_count} for uid, usage_count in scale_usage
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.remove()

@api.route('/api/users/all')
@login_required
def get_users():
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    db = get_db()

    users = [user.as_dict() for user in db.query(models.Usuario).filter(models.Usuario.username != 'admin').all()]
    db.remove()
    return jsonify(users)

@api.route('/api/users/<username>')
@login_required
def get_user(username: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    db = get_db()

    user = db.query(models.Usuario).filter_by(username=username).first()
    db.remove()
    return jsonify(user.as_dict())

@api.route('/api/users/me')
@login_required
def get_me():
    return jsonify(current_user.as_dict())

@api.route('/api/users/update/<username>', methods=['POST'])
def update_user(username: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    db = get_db()
    data = request.get_json()

    user = db.query(models.Usuario).filter_by(username=username).first()
    if not user:
        return jsonify('O usuário não existe no banco de dados.'), 404

    # Check for username conflict (if changing username)
    if 'username' in data and data['username'] != username:
        existing_user = db.query(models.Usuario).filter_by(username=data['username']).first()
        if existing_user:
            return jsonify('Este username já está em uso.'), 409

    # Check for email conflict (if changing email)
    if 'email' in data and data['email'] != user.email:
        if data['email'] is not None:  # Only check if email is being set
            existing = db.query(models.Usuario).filter_by(email=data['email']).first()
            if existing:
                return jsonify('Este email já está em uso'), 409

    # Update non-password fields
    if 'username' in data:
        user.username = data['username']
    if 'nome_completo' in data:
        user.nome_completo = data['nome_completo']
    if 'email' in data:
        user.email = data['email']
    if 'pfp_url' in data:
        user.pfp_url = data['pfp_url']

    # Update password (if provided)
    if 'new_password' in data and data['new_password']:
        salt = bcrypt.gensalt(rounds=12)
        salt_str = b64encode(salt).decode('utf-8')
        key = bcrypt.kdf(
            password=data['new_password'].encode(),
            salt=salt,
            desired_key_bytes=32,
            rounds=100
        )
        key_str = b64encode(key).decode('utf-8')
        user.key = key_str
        user.salt = salt_str

    try:
        db.commit()
        return jsonify(user.as_dict())
    except IntegrityError as e:
        db.rollback()
        return jsonify({'error': 'Conflito de dados únicos (username/email já existe)'}), 409
    finally:
        db.remove()

@api.route('/api/users/ban/<username>')
def ban_user(username: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    db = get_db()

    user = db.query(models.Usuario).filter_by(username=username).first()

    if not user:
        abort(404, description='O usuário nao existe no banco de dados.')

    stmt = ()

    if (user.status == 'Ativo'):
        stmt = (
            update(models.Usuario)
            .where(models.Usuario.username == username)
            .values(status='Banido')
        )
    else:
        stmt = (
            update(models.Usuario)
            .where(models.Usuario.username == username)
            .values(status='Ativo')
        )

    db.execute(stmt)
    db.commit()
    db_user = db.query(models.Usuario).filter_by(username=username).first()
    db.remove()
    return jsonify(db_user.as_dict())

@api.route('/api/users/delete/<username>')
@login_required
def del_user(username: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    db = get_db()

    rows_affected = db.query(models.Usuario).filter(models.Usuario.username == username).delete()

    res = {
        'rowsAffected': rows_affected
    }
   
    db.commit()
    db.remove()
    return jsonify(res)

@api.route('/api/users/register/', methods=['POST'])
@login_required
def register_user():
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    fullname = request.form.get('fullname')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    db = get_db()

    user = db.query(models.Usuario).filter_by(username=username).first()

    if user:
        flash('Este nome de usuário já está em uso.')
        return redirect(url_for('main.register_user'))
    
    user = db.query(models.Usuario).filter_by(email=email).first()

    if user:
        flash('Este email já está em uso.')
        return redirect(url_for('main.register_user'))
    
    salt = bcrypt.gensalt(rounds=12)
    salt_str = b64encode(salt).decode('utf-8')
    key = bcrypt.kdf(password=password.encode(), salt=salt, desired_key_bytes=32, rounds=100)
    key_str = b64encode(key).decode('utf-8')

    usuario = models.Usuario(
        username=username,
        nome_completo=fullname,
        email=email,
        privilegios='Usuário',
        salt=salt_str, key=key_str
    )
    
    db.add(usuario)
    db.commit()
    db.flush()

    db.remove()
    return redirect(url_for('main.list_users'))

@api.route('/api/scales/all')
@login_required
def get_scales():
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    db = get_db()

    scales = [user.as_dict() for user in db.query(models.Balanca).all()]
    db.remove()
    return jsonify(scales)

@api.route('/api/scales/delete/<uid>', methods=['DELETE'])
@login_required
def del_scale(uid: str):
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    db = get_db()

    rows_affected = db.query(models.Balanca).filter(models.Balanca.uid == uid).delete()

    res = {
        'rowsAffected': rows_affected
    }
   
    db.commit()
    db.remove()
    return jsonify(res)

@api.route('/api/scales/<uid>')
@login_required
def get_scale(uid: str):
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))
    
    db = get_db()

    scale = db.query(models.Balanca).filter_by(uid=uid).first()

    db.remove()
    if not scale:
        abort(404, message='A balança solicitada não existe.')

    return jsonify(scale.as_dict())

@api.route('/api/scales/register/', methods=['POST'])
@login_required
def register_scale():
    if current_user.privilegios != 'Administrador':
        abort(401, description='Permissões insuficientes.')

    uid = request.form.get('uid')
    obs = request.form.get('obs')

    if uid:
        uid = uid.lower()

    db = get_db()

    scale = db.query(models.Balanca).filter_by(uid=uid).first()

    if scale:
        flash('Este identificador único já foi usado por outra balança')
        return redirect(url_for('main.register_scale'))

    db_scale = models.Balanca(
        uid=uid,
        status='Offline',
        observacoes=obs
    )
    
    db.add(db_scale)
    db.commit()
    db.flush()

    db.remove()
    return redirect(url_for('main.list_scales'))

@api.route('/api/scales/<uid>/command/<command>')
@login_required
def scale_command(uid, command):
    if current_user.status == 'Banido':
        flash('O usuário foi banido por tempo indeterminado.')
        return redirect(url_for('auth.login'))

    data = {
        'uid': uid,
        'command': command
    }

    if command == 'TARE':
        db = get_db()
        stmt = (
            update(models.Balanca)
            .where(models.Balanca.uid == uid)
            .values(ultima_calibragem=func.current_timestamp())
        )

        db.execute(stmt)
        db.commit()
        db.remove()

    res = json.dumps(data)

    current_app.extensions['mqtt'].publish('cow8/commands', res)

    return jsonify(data)

@api.route('/api/chatbot/prompt/', methods=['POST'])
@login_required
def prompt_chatbot():
    data = request.get_json()

    if 'content' not in data:
        return jsonify({'message': 'Invalid Payload.'}), 422

    res, sql = current_app.extensions['ai'].ask_about_data(data['content'])

    return jsonify({'response': res, 'sql': sql})