from typing import Optional, Set

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, CHAR, ForeignKey

from .base import Base
from .database import get_db

class Animal(Base):
    __tablename__ = 'Animal'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uid : Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    sexo : Mapped[str] = mapped_column(CHAR(1), nullable=False)
    id_dados_animal : Mapped[int] = mapped_column(ForeignKey('CategoriaAnimal.id'))

    dados_animal : Mapped['CategoriaAnimal'] = relationship(
        back_populates='animais',
    )

    pesagens : Mapped[Optional[Set['RegistroPesagem']]] = relationship(
        back_populates='animal', cascade='all, delete-orphan'
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"""Animal(
            id={self.id!r},
            uid={self.uid!r},
            sexo={self.sexo!r},
            id_dados_animal={self.id_dados_animal!r}
        )"""
    
    @staticmethod
    def get_all_animais():
        db = get_db()
        animais = db.query(Animal).all()
        db.remove()
        return animais

    @staticmethod
    def get_animal_by_uid(uid: str):
        db = get_db()
        animal = db.query(Animal).filter_by(uid=uid).first()
        db.remove()
        return animal