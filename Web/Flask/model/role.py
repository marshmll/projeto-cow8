from typing import Optional, Set

from sqlalchemy import UniqueConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.database import Base, get_db

class Role(Base):
    __tablename__ = 'Role'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name : Mapped[str] = mapped_column(String(50), nullable=False, default='Usuário')

    usuarios : Mapped[Optional[Set['Usuario']]] = relationship(
        back_populates='role', cascade='all, delete-orphan'
    )

    __table_args__ = (
        UniqueConstraint('name', name='uq_name'),
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f'''Role(
            id={self.id!r},
            name={self.name!r},
        )'''

    @staticmethod
    def get_role_by_id(id: int):
        db = get_db()
        role = db.query(Role).filter_by(id=id).first()
        db.remove()
        return role

    @staticmethod
    def get_role_by_name(name: str):
        db = get_db()
        role = db.query(Role).filter_by(name=name).first()
        db.remove()
        return role
    
    @staticmethod
    def create_role(name: str):
        db = get_db()
        role = Role(name=name)
        db.add(role)
        db.commit()
        db.flush()
        db.remove()
        return role