from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Integer, DateTime, func, update

from .base import Base
from model.database import get_db

class Balanca(Base):
    __tablename__ = 'Balanca'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uid : Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    datahora_registro : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.current_timestamp())
    ultima_calibragem : Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ultima_comunicacao : Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status : Mapped[str] = mapped_column(String(50), nullable=False, default="Offline")
    observacoes : Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"""Balanca(
            id={self.id!r},
            uid={self.uid!r},
            datahora_registro={self.datahora_registro!r},
            ultima_calibragem={self.ultima_calibragem!r},
            ultima_comunicacao={self.ultima_comunicacao!r},
            status={self.status!r},
            observacoes={self.observacoes!r}
        )"""
    
    @staticmethod
    def get_all_balancas():
        db = get_db()
        balancas = db.query(Balanca).all()
        db.remove()
        return balancas

    @staticmethod
    def get_balanca_by_uid(uid: str):
        db = get_db()
        scale = db.query(Balanca).filter_by(uid=uid).first()
        db.remove()
        return scale if scale else None

    @staticmethod
    def create_balanca(uid: str, status: str, observacoes: str):
        db = get_db()
        scale = Balanca(
            uid=uid,
            status=status,
            observacoes=observacoes
        )
        db.add(scale)
        db.commit()
        db.flush()
        db.remove()


    @staticmethod
    def update_ultima_calibragem(uid: str):
        db = get_db()
        stmt = (
            update(Balanca)
            .where(Balanca.uid == uid)
            .values(ultima_calibragem=func.current_timestamp(), ultima_comunicacao=func.current_timestamp())
        )

        db.execute(stmt)
        db.commit()
        db.remove()

    @staticmethod
    def update_status(data):
        db = get_db()
        stmt = (
            update(Balanca)
            .where(Balanca.uid == data['uid'])
            .values(status=data['status'], ultima_comunicacao=func.current_timestamp())
        )
        db.execute(stmt)
        db.commit()
        db.remove()

    @staticmethod
    def delete_balanca_by_uid(uid: str):
        db = get_db()

        rows_affected = db.query(Balanca).filter(Balanca.uid == uid).delete()

        res = {
            'rowsAffected': rows_affected
        }
    
        db.commit()
        db.remove()
        return res