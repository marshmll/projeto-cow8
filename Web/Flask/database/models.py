from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, Numeric, DateTime, ForeignKey, CHAR, UniqueConstraint, func
from datetime import datetime
from typing import Optional, Set
from flask_login import UserMixin

Base = declarative_base()

class Usuario(Base, UserMixin):
    __tablename__ = 'Usuario'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username : Mapped[str] = mapped_column(String(120), nullable=False)
    nome_completo : Mapped[str] = mapped_column(Text, nullable=False)
    email : Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    pfp_url : Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    datahora_registro : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    status : Mapped[str] = mapped_column(String(50), nullable=False, default="Ativo")
    privilegios : Mapped[str] = mapped_column(String(50), nullable=False, default="Usuário")
    key : Mapped[str] = mapped_column(Text, nullable=False)
    salt : Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("username", "email", name="user_identity"),)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"""Usuario(
            id={self.id!r},
            username={self.username!r},
            nome_completo={self.nome_completo!r},
            datahora_registro={self.datahora_registro!r},
            status={self.status!r},
            privilegios={self.privilegios!r},
            key={self.key!r},
            salt={self.salt!r}
        )"""


class Balanca(Base):
    __tablename__ = 'Balanca'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uid : Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    datahora_registro : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    status : Mapped[str] = mapped_column(String(50), nullable=False, default="Operacional")
    observacoes : Mapped[str] = mapped_column(Text, nullable=True)

    pesagens : Mapped[Optional[Set["ControlePesagem"]]] = relationship(
        back_populates="balanca", cascade="all, delete-orphan"
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"""Balanca(
            id={self.id!r},
            uid={self.uid!r},
            datahora_registro={self.datahora_registro!r},
            status={self.status!r},
            observacoes={self.observacoes!r}
        )"""


class DadosAnimal(Base):
    __tablename__ = 'DadosAnimal'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    raca : Mapped[str] = mapped_column(String(50), nullable=False)
    peso_medio : Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)

    animais : Mapped[Optional[Set["Animal"]]] = relationship(
        back_populates="dados_animal", cascade="all, delete-orphan"
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"""DadosAnimal(
            id={self.id!r},
            raca={self.raca!r},
            peso_medio={self.peso_medio!r}
        )"""

class Animal(Base):
    __tablename__ = 'Animal'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uid : Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    sexo : Mapped[str] = mapped_column(CHAR(1), nullable=False)
    id_dados_animal : Mapped[int] = mapped_column(ForeignKey("DadosAnimal.id"))

    dados_animal : Mapped["DadosAnimal"] = relationship(
        back_populates="animais",
    )

    pesagens : Mapped[Optional[Set['ControlePesagem']]] = relationship(
        back_populates="animal", cascade="all, delete-orphan"
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

class ControlePesagem(Base):
    __tablename__ = "ControlePesagem"

    id_animal : Mapped[int] = mapped_column(ForeignKey("Animal.id"), nullable=False, primary_key=True)
    id_balanca : Mapped[int] = mapped_column(ForeignKey("Balanca.id"), nullable=False, primary_key=True)
    datahora_pesagem : Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False, primary_key=True)
    medicao_peso : Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    observacoes : Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    animal : Mapped['Animal'] = relationship(
        back_populates="pesagens",
    )

    balanca : Mapped['Balanca'] = relationship(
        back_populates="pesagens",
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"""ControlePesagem(
            id_animal={self.id_animal!r},
            datahora_pesagem={self.datahora_pesagem!r},
            medicao_peso={self.medicao_peso!r},
            observacoes={self.observacoes!r}
        )"""
