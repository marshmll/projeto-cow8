from datetime import datetime

from sqlalchemy import extract, func

from model.database import get_db
from model.registro_pesagem import RegistroPesagem

class Means():
    @staticmethod
    def get_means():
        # Consulta para obter o peso médio por mês
        db = get_db()
        current_year = datetime.now().year
        monthly_avg = db.query(
            extract('month', RegistroPesagem.datahora_pesagem).label('month'),
            func.avg(RegistroPesagem.medicao_peso).label('avg_weight')
        ).filter(
            extract('year', RegistroPesagem.datahora_pesagem) == current_year
        ).group_by(
            extract('month', RegistroPesagem.datahora_pesagem)
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
        return monthly_data