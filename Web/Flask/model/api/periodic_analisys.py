from datetime import datetime

from sqlalchemy import func, distinct, exists, case

from model.database import get_db
from model.registro_pesagem import RegistroPesagem
from model.animal import Animal
from model.categoria_animal import CategoriaAnimal
from model.balanca import Balanca

class PeriodicAnalisys():
    @staticmethod
    def get_periodic_analisys(start_datetime: datetime, end_datetime: datetime):
        db = get_db()

        # Weight statistics
        weight_query = db.query(
            func.avg(RegistroPesagem.medicao_peso),
            func.min(RegistroPesagem.medicao_peso),
            func.max(RegistroPesagem.medicao_peso),
            func.count(RegistroPesagem.datahora_pesagem)
        ).filter(
            RegistroPesagem.datahora_pesagem >= start_datetime,
            RegistroPesagem.datahora_pesagem <= end_datetime
        ).first()
        avg_weight, min_weight, max_weight, weight_count = weight_query or (0, 0, 0, 0)

        # Total animals and underweight count
        total_animals = db.query(func.count(Animal.id)).scalar() or 0
        underweight_count = db.query(
            func.count(distinct(RegistroPesagem.id_animal))
        ).join(
            Animal, Animal.id == RegistroPesagem.id_animal
        ).join(
            CategoriaAnimal, CategoriaAnimal.id == Animal.id_dados_animal
        ).filter(
            RegistroPesagem.datahora_pesagem >= start_datetime,
            RegistroPesagem.datahora_pesagem <= end_datetime,
            RegistroPesagem.medicao_peso < CategoriaAnimal.peso_medio * 0.9
        ).scalar() or 0

       # Animal trend classification
        trend_subquery = db.query(
            Animal.id,
            case(
                # Gaining if ANY measurement is >105% of average
                (exists().where(
                    RegistroPesagem.id_animal == Animal.id,
                    RegistroPesagem.medicao_peso > CategoriaAnimal.peso_medio * 1.05,
                    RegistroPesagem.datahora_pesagem >= start_datetime,
                    RegistroPesagem.datahora_pesagem <= end_datetime
                ), 'gaining'),
                # Losing if ANY measurement is <95% of average AND NONE are >105%
                (exists().where(
                    RegistroPesagem.id_animal == Animal.id,
                    RegistroPesagem.medicao_peso < CategoriaAnimal.peso_medio * 0.95,
                    RegistroPesagem.datahora_pesagem >= start_datetime,
                    RegistroPesagem.datahora_pesagem <= end_datetime
                ) & ~exists().where(
                    RegistroPesagem.id_animal == Animal.id,
                    RegistroPesagem.medicao_peso > CategoriaAnimal.peso_medio * 1.05,
                    RegistroPesagem.datahora_pesagem >= start_datetime,
                    RegistroPesagem.datahora_pesagem <= end_datetime
                ), 'losing'),
                # Stable if ALL measurements are between 95%-105% of average
                else_='stable'
            ).label('trend')
        ).join(
            CategoriaAnimal, CategoriaAnimal.id == Animal.id_dados_animal
        ).filter(
            exists().where(
                RegistroPesagem.id_animal == Animal.id,
                RegistroPesagem.datahora_pesagem >= start_datetime,
                RegistroPesagem.datahora_pesagem <= end_datetime
            )
        ).subquery()

        trend_counts = db.query(
            func.sum(case((trend_subquery.c.trend == 'gaining', 1), else_=0)).label('gaining_count'),
            func.sum(case((trend_subquery.c.trend == 'losing', 1), else_=0)).label('losing_count'),
            func.sum(case((trend_subquery.c.trend == 'stable', 1), else_=0)).label('stable_count')
        ).select_from(trend_subquery).first()

        # Breed distribution
        breed_distribution = db.query(
            CategoriaAnimal.raca,
            func.count(Animal.id)
        ).join(
            Animal, Animal.id_dados_animal == CategoriaAnimal.id
        ).group_by(CategoriaAnimal.raca).all()

        # Scale usage
        scale_usage = db.query(
            Balanca.uid,
            func.count(RegistroPesagem.uid_balanca)
        ).join(
            RegistroPesagem, RegistroPesagem.uid_balanca == Balanca.uid
        ).filter(
            RegistroPesagem.datahora_pesagem >= start_datetime,
            RegistroPesagem.datahora_pesagem <= end_datetime
        ).group_by(Balanca.uid).all()
    
        db.remove()

        return {
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
        }

    