from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, func

from .base import Base
from .database import get_db

class RegistroPesagem(Base):
    __tablename__ = 'RegistroPesagem'

    id_animal : Mapped[int] = mapped_column(ForeignKey('Animal.id'), nullable=False, primary_key=True)
    uid_balanca : Mapped[str] = mapped_column(String(120), nullable=False, primary_key=True)
    datahora_pesagem : Mapped[datetime] = mapped_column(DateTime, default=func.current_timestamp(), nullable=False, primary_key=True)
    medicao_peso : Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    observacoes : Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    animal : Mapped['Animal'] = relationship(
        back_populates='pesagens',
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"""RegistroPesagem(
            id_animal={self.id_animal!r},
            uid_balanca={self.uid_balanca!r},
            datahora_pesagem={self.datahora_pesagem!r},
            medicao_peso={self.medicao_peso!r},
            observacoes={self.observacoes!r}
        )"""
    
    @staticmethod
    def get_all_registros():
        db = get_db()
        registros = db.query(RegistroPesagem).all()
        db.remove()
        return registros

    @staticmethod
    def create_registro(id_animal, uid_balanca, medicao_peso):
        db = get_db()
        record = RegistroPesagem(
            id_animal=id_animal,
            uid_balanca=uid_balanca,
            medicao_peso=medicao_peso
        )

        db.add(record)
        db.commit()
        db.flush()
        db.remove()

