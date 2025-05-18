from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Integer
from typing import Optional, Set

class CategoriaAnimal(Base):
    __tablename__ = 'CategoriaAnimal'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    raca : Mapped[str] = mapped_column(String(50), nullable=False)
    peso_medio : Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)

    animais : Mapped[Optional[Set["Animal"]]] = relationship(
        back_populates="dados_animal", cascade="all, delete-orphan"
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"""CategoriaAnimal(
            id={self.id!r},
            raca={self.raca!r},
            peso_medio={self.peso_medio!r}
        )"""