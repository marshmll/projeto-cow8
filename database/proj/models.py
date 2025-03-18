from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, Numeric, Date, DateTime, ForeignKey, UniqueConstraint, CHAR
from datetime import date, datetime
from typing import Optional, Set

Base = declarative_base()

class DadosAnimal(Base):
    __tablename__ = 'DadosAnimal'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    raca : Mapped[str] = mapped_column(String(50), nullable=False)
    peso_medio : Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)

    animais : Mapped[Optional[Set["Animal"]]] = relationship(
        back_populates="dados_animal", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"""DadosAnimal(
            id={self.id!r},
            raca={self.raca!r},
            peso_medio={self.peso_medio!r}
        )"""

class Animal(Base):
    __tablename__ = 'Animal'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sexo : Mapped[str] = mapped_column(CHAR(1), nullable=False)
    id_dados_animal : Mapped[int] = mapped_column(ForeignKey("DadosAnimal.id"))

    dados_animal : Mapped["DadosAnimal"] = relationship(
        back_populates="animais",
    )

    def __repr__(self):
        return f"""Animal(
            id={self.id!r},
            sexo={self.sexo!r},
            id_dados_animal={self.id_dados_animal!r}
        )"""

class ControlePesagem(Base):
    __tablename__ = "ControlePesagem"

    id_animal : Mapped[int] = mapped_column(ForeignKey("Animal.id"), nullable=False, primary_key=True)
    datahora_pesagem : Mapped[datetime] = mapped_column(DateTime, default="CURRENT_DATETIME()", nullable=False, primary_key=True)
    medicao_peso : Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    observacoes : Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"""ControlePesagem(
            id_animal={self.id_animal!r},
            datahora_pesagem={self.datahora_pesagem!r},
            medicao_peso={self.medicao_peso!r},
            observacoes={self.observacoes!r}
        )"""
