from datetime import datetime, timedelta

from sqlalchemy import func

from model.database import get_db
from model.registro_pesagem import RegistroPesagem
from model.categoria_animal import CategoriaAnimal
from model.animal import Animal

class HealthStatus():
    @staticmethod
    def get_health_status():
        db = get_db()
    
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
            RegistroPesagem.id_animal,
            func.min(RegistroPesagem.datahora_pesagem).label('first_date')
        ).filter(
            RegistroPesagem.datahora_pesagem >= start_of_month,
            RegistroPesagem.datahora_pesagem < start_of_next_month
        ).group_by(
            RegistroPesagem.id_animal
        ).subquery()

        # Subquery: última pesagem do mês
        last_weights_subq = db.query(
            RegistroPesagem.id_animal,
            func.max(RegistroPesagem.datahora_pesagem).label('last_date')
        ).filter(
            RegistroPesagem.datahora_pesagem >= start_of_month,
            RegistroPesagem.datahora_pesagem < start_of_next_month
        ).group_by(
            RegistroPesagem.id_animal
        ).subquery()

        # Recuperar pesos associados
        first_weights = db.query(
            RegistroPesagem.id_animal,
            RegistroPesagem.medicao_peso,
            RegistroPesagem.datahora_pesagem
        ).join(
            first_weights_subq,
            (RegistroPesagem.id_animal == first_weights_subq.c.id_animal) &
            (RegistroPesagem.datahora_pesagem == first_weights_subq.c.first_date)
        ).all()

        last_weights = db.query(
            RegistroPesagem.id_animal,
            RegistroPesagem.medicao_peso,
            RegistroPesagem.datahora_pesagem
        ).join(
            last_weights_subq,
            (RegistroPesagem.id_animal == last_weights_subq.c.id_animal) &
            (RegistroPesagem.datahora_pesagem == last_weights_subq.c.last_date)
        ).all()

        first_map = {fw.id_animal: (float(fw.medicao_peso), fw.datahora_pesagem) for fw in first_weights}
        last_map = {lw.id_animal: (float(lw.medicao_peso), lw.datahora_pesagem) for lw in last_weights}

        # Pega dados dos animais
        animals_data = db.query(
            Animal.id,
            CategoriaAnimal.peso_medio
        ).join(
            CategoriaAnimal, Animal.id_dados_animal == CategoriaAnimal.id
        ).all()

        if not animals_data:
            return {'health_status': 100, 'message': 'Nenhum animal cadastrado'}

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

        db.remove()

        return {
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
        }
