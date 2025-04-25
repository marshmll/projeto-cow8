from flask import Blueprint, jsonify, abort, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from database.database import get_db
from database import models
from datetime import datetime, timedelta
from sqlalchemy import extract, func, distinct, update
import locale
import bcrypt
import json
from base64 import b64encode
locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

api = Blueprint('api', __name__)

@api.route('/api/means')
@login_required
def get_means():
    if current_user.status == "Banido":
        flash("O usuário foi banido por tempo indeterminado.")
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
    if current_user.status == "Banido":
        flash("O usuário foi banido por tempo indeterminado.")
        return redirect(url_for('auth.login'))

    current_year = datetime.now().year
    db = get_db()
    
    # 1. Consulta animais com peso abaixo de 90% da média da raça por mês
    underweight_animals = db.query(
        extract('month', models.ControlePesagem.datahora_pesagem).label('month'),
        func.count(distinct(models.ControlePesagem.id_animal)).label('count')
    ).join(
        models.Animal, models.Animal.id == models.ControlePesagem.id_animal
    ).join(
        models.DadosAnimal, models.DadosAnimal.id == models.Animal.id_dados_animal
    ).filter(
        extract('year', models.ControlePesagem.datahora_pesagem) == current_year,
        models.ControlePesagem.medicao_peso < (models.DadosAnimal.peso_medio * 0.9)
    ).group_by(
        extract('month', models.ControlePesagem.datahora_pesagem)
    ).all()

    # 2. Consulta animais com perda de peso entre pesagens consecutivas
    weight_loss_subquery = db.query(
        models.ControlePesagem.id_animal,
        extract('month', models.ControlePesagem.datahora_pesagem).label('month'),
        (models.ControlePesagem.medicao_peso - func.lag(models.ControlePesagem.medicao_peso).over(
            partition_by=models.ControlePesagem.id_animal,
            order_by=models.ControlePesagem.datahora_pesagem
        )).label('weight_diff')
    ).filter(
        extract('year', models.ControlePesagem.datahora_pesagem) == current_year
    ).subquery()

    weight_loss_animals = db.query(
        weight_loss_subquery.c.month,
        func.count(distinct(weight_loss_subquery.c.id_animal)).label('count')
    ).filter(
        weight_loss_subquery.c.weight_diff < 0
    ).group_by(
        weight_loss_subquery.c.month
    ).all()

    # Combina os resultados
    health_metrics = []
    for month in range(1, 13):
        # Animais abaixo do peso
        underweight = next((item.count for item in underweight_animals if item.month == month), 0)
        
        # Animais com perda de peso
        weight_loss = next((item.count for item in weight_loss_animals if item.month == month), 0)
        
        # Total de animais com problemas
        total = underweight + weight_loss
        
        health_metrics.append({
            'month': month,
            'month_name': datetime(current_year, month, 1).strftime('%B'),
            'underweight_count': underweight,
            'weight_loss_count': weight_loss,
            'total_at_risk': total
        })
    db.remove()
    return jsonify(health_metrics)

@api.route('/api/health_status')
@login_required
def get_health_status():
    if current_user.status == "Banido":
        flash("O usuário foi banido por tempo indeterminado.")
        return redirect(url_for('auth.login'))
    
    current_year = datetime.now().year
    db = get_db()

    animals = db.query(models.Animal).all()
    total_animals = len(animals)
    
    if total_animals == 0:
        db.remove()
        return jsonify({"health_status": 100, "message": "Nenhum animal cadastrado"})
    
    healthy = warning = critical = 0

    for animal in animals:
        # Obter todas as pesagens do ano atual
        weights = db.query(models.ControlePesagem)\
            .filter(models.ControlePesagem.id_animal == animal.id)\
            .filter(extract('year', models.ControlePesagem.datahora_pesagem) == current_year)\
            .order_by(models.ControlePesagem.datahora_pesagem.asc())\
            .all()
        
        if not weights:
            continue
            
        # Converter para float para evitar problemas com Decimal
        first_weight = float(weights[0].medicao_peso)
        last_weight = float(weights[-1].medicao_peso)
        
        breed_data = db.query(models.DadosAnimal)\
            .filter(models.DadosAnimal.id == animal.id_dados_animal)\
            .first()
        
        if not breed_data:
            continue
            
        # Converter peso médio para float
        expected_final_weight = float(breed_data.peso_medio)
        
        # 1. Calcular progresso esperado (considerando crescimento linear durante o ano)
        months_passed = (datetime.now().month - weights[0].datahora_pesagem.month) or 1
        expected_progress = expected_final_weight - first_weight
        expected_weight = first_weight + (expected_progress * (months_passed/12))
        
        # 2. Análise de tendência (últimos 3 meses)
        trend = 0
        three_months_ago = datetime.now() - timedelta(days=90)
        last_months_weights = [
            float(w.medicao_peso) for w in weights 
            if w.datahora_pesagem >= three_months_ago
        ]
        
        if len(last_months_weights) >= 2:
            initial_weight = last_months_weights[0]
            final_weight = last_months_weights[-1]
            trend = ((final_weight - initial_weight) / initial_weight) * 100  # % de variação
        
        # 3. Classificação
        weight_ratio = last_weight / expected_weight
        
        if weight_ratio >= 0.95 and trend >= -1:  # Saudável
            healthy += 1
        elif weight_ratio >= 0.85 or (weight_ratio >= 0.9 and trend >= -3):  # Em alerta
            warning += 1
        else:  # Crítico
            critical += 1
    
    # Calcular porcentagem de saúde
    health_score = (
        (healthy * 1.0 + warning * 0.6 + critical * 0.2) / 
        max(1, total_animals) * 100  # Evita divisão por zero
    )
    
    db.remove()

    return jsonify({
        "health_status": round(health_score, 2),
        "healthy_animals": healthy,
        "warning_animals": warning,
        "critical_animals": critical,
        "total_animals": total_animals,
        "metrics": {
            "calculation_date": datetime.now().isoformat(),
            "weight_ratio_thresholds": {
                "healthy": "≥95%",
                "warning": "85-94%",
                "critical": "<85%"
            },
            "trend_thresholds": {
                "healthy": "≥-1%",
                "warning": "-1% to -3%",
                "critical": "<-3%"
            }
        }
    })

@api.route('/api/users/all')
@login_required
def get_users():
    if current_user.privilegios != "Administrador":
        abort(401, description="Permissões insuficientes.")

    db = get_db()

    users = [user.as_dict() for user in db.query(models.Usuario).filter(models.Usuario.username != "admin").all()]
    db.remove()
    return jsonify(users)

@api.route('/api/users/ban/<username>')
def ban_user(username: str):
    if current_user.privilegios != "Administrador":
        abort(401, description="Permissões insuficientes.")

    db = get_db()

    user = db.query(models.Usuario).filter_by(username=username).first()

    if not user:
        abort(404, description="O usuário nao existe no banco de dados.")

    stmt = ()

    if (user.status == "Ativo"):
        stmt = (
            update(models.Usuario)
            .where(models.Usuario.username == username)
            .values(status="Banido")
        )
    else:
        stmt = (
            update(models.Usuario)
            .where(models.Usuario.username == username)
            .values(status="Ativo")
        )

    db.execute(stmt)
    db.commit()
    db_user = db.query(models.Usuario).filter_by(username=username).first()
    db.remove()
    return jsonify(db_user.as_dict())

@api.route('/api/users/delete/<username>')
@login_required
def del_user(username: str):
    if current_user.privilegios != "Administrador":
        abort(401, description="Permissões insuficientes.")

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
    if current_user.privilegios != "Administrador":
        abort(401, description="Permissões insuficientes.")

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
    if current_user.privilegios != "Administrador":
        abort(401, description="Permissões insuficientes.")

    db = get_db()

    scales = [user.as_dict() for user in db.query(models.Balanca).all()]
    db.remove()
    return jsonify(scales)

@api.route('/api/scales/delete/<uid>', methods=['DELETE'])
@login_required
def del_scale(uid: str):
    if current_user.privilegios != "Administrador":
        abort(401, description="Permissões insuficientes.")

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
    if current_user.privilegios != "Administrador":
        abort(401, description="Permissões insuficientes.")

    db = get_db()

    scale = db.query(models.Balanca).filter_by(uid=uid).first()

    db.remove()
    if not scale:
        abort(404, message="A balança solicitada não existe.")

    return jsonify(scale.as_dict())

@api.route('/api/scales/register/', methods=['POST'])
@login_required
def register_scale():
    if current_user.privilegios != "Administrador":
        abort(401, description="Permissões insuficientes.")

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
        status="Offline",
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
    data = {
        'uid': uid,
        'command': command
    }

    if command == "TARE":
        db = get_db()
        stmt = (
            update(models.Balanca)
            .where(models.Balanca.uid == uid)
            .values(ultima_calibragem=func.now())
        )

        db.execute(stmt)
        db.commit()
        db.remove()

    j = json.dumps(data)

    current_app.extensions['mqtt'].publish('cow8/commands', j)

    return jsonify(data)
