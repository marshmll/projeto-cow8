from datetime import datetime

from sqlalchemy import extract, func

from model.database import get_db
from model.registro_pesagem import RegistroPesagem
from model.categoria_animal import CategoriaAnimal
from model.animal import Animal

class HealthMetrics():
    @staticmethod
    def get_health_metrics():
        current_year = datetime.now().year
        db = get_db()
    
        # 1. Subquery para a última pesagem de cada animal em cada mês
        last_weight_subq = db.query(
            RegistroPesagem.id_animal,
            extract('month', RegistroPesagem.datahora_pesagem).label('month'),
            func.max(RegistroPesagem.datahora_pesagem).label('last_date')
        ).filter(
            extract('year', RegistroPesagem.datahora_pesagem) == current_year
        ).group_by(
            RegistroPesagem.id_animal,
            extract('month', RegistroPesagem.datahora_pesagem)
        ).subquery()

        # 2. Junta a última pesagem com o peso médio da raça
        last_weights = db.query(
            last_weight_subq.c.id_animal,
            last_weight_subq.c.month,
            RegistroPesagem.medicao_peso,
            CategoriaAnimal.peso_medio
        ).join(
            RegistroPesagem,
            (RegistroPesagem.id_animal == last_weight_subq.c.id_animal) &
            (RegistroPesagem.datahora_pesagem == last_weight_subq.c.last_date)
        ).join(
            Animal, Animal.id == RegistroPesagem.id_animal
        ).join(
            CategoriaAnimal, CategoriaAnimal.id == Animal.id_dados_animal
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
            RegistroPesagem.id_animal,
            extract('month', RegistroPesagem.datahora_pesagem).label('month'),
            (RegistroPesagem.medicao_peso - func.lag(RegistroPesagem.medicao_peso).over(
                partition_by=[
                    RegistroPesagem.id_animal,
                    extract('month', RegistroPesagem.datahora_pesagem)
                ],
                order_by=RegistroPesagem.datahora_pesagem
            )).label('weight_diff')
        ).filter(
            extract('year', RegistroPesagem.datahora_pesagem) == current_year
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

        db.remove()
        return health_metrics