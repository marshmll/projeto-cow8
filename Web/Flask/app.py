from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import os
from database.database import SessionLocal, Base, engine
from database import models
import json
from datetime import datetime, timedelta
from sqlalchemy import extract, func, distinct
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

app = Flask(__name__)

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "flask/test"

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

def init_db():
    Base.metadata.create_all(bind=engine)

@app.route('/')
def index():
    data = {}
    data["animal_count"] = len(SessionLocal.query(models.Animal).all())
    data["measurement_count"] = len(SessionLocal.query(models.ControlePesagem).all())
    
    return render_template('index.html', data=data)

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/means')
def get_means():
    # Consulta para obter o peso médio por mês
    current_year = datetime.now().year
    monthly_avg = SessionLocal.query(
        extract('month', models.ControlePesagem.datahora_pesagem).label('month'),
        func.avg(models.ControlePesagem.medicao_peso).label('avg_weight')
    ).filter(
        extract('year', models.ControlePesagem.datahora_pesagem) == current_year
    ).group_by(
        extract('month', models.ControlePesagem.datahora_pesagem)
    ).all()
    
    # Criar uma lista com todos os meses do ano (meses sem dados terão valor None)
    monthly_data = []
    for month in range(1, 13):
        avg_weight = next((item.avg_weight for item in monthly_avg if item.month == month), None)
        monthly_data.append({
            'month': month,
            'month_name': datetime(current_year, month, 1).strftime('%B'),
            'avg_weight': float(avg_weight) if avg_weight is not None else 0
        })

    return jsonify(monthly_data)
    
@app.route('/health_metrics')
def get_health_metrics():
    current_year = datetime.now().year
    
    # 1. Consulta animais com peso abaixo de 90% da média da raça por mês
    underweight_animals = SessionLocal.query(
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
    weight_loss_subquery = SessionLocal.query(
        models.ControlePesagem.id_animal,
        extract('month', models.ControlePesagem.datahora_pesagem).label('month'),
        (models.ControlePesagem.medicao_peso - func.lag(models.ControlePesagem.medicao_peso).over(
            partition_by=models.ControlePesagem.id_animal,
            order_by=models.ControlePesagem.datahora_pesagem
        )).label('weight_diff')
    ).filter(
        extract('year', models.ControlePesagem.datahora_pesagem) == current_year
    ).subquery()

    weight_loss_animals = SessionLocal.query(
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

    return jsonify(health_metrics)

@app.route('/health_status')
def get_health_status():
    current_year = datetime.now().year
    animals = SessionLocal.query(models.Animal).all()
    total_animals = len(animals)
    
    if total_animals == 0:
        return jsonify({"health_status": 100, "message": "Nenhum animal cadastrado"})
    
    healthy = warning = critical = 0

    for animal in animals:
        # Obter todas as pesagens do ano atual
        weights = SessionLocal.query(models.ControlePesagem)\
            .filter(models.ControlePesagem.id_animal == animal.id)\
            .filter(extract('year', models.ControlePesagem.datahora_pesagem) == current_year)\
            .order_by(models.ControlePesagem.datahora_pesagem.asc())\
            .all()
        
        if not weights:
            continue
            
        # Converter para float para evitar problemas com Decimal
        first_weight = float(weights[0].medicao_peso)
        last_weight = float(weights[-1].medicao_peso)
        
        breed_data = SessionLocal.query(models.DadosAnimal)\
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

@app.teardown_appcontext
def shutdown_session(exception=None):
    SessionLocal.remove()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
