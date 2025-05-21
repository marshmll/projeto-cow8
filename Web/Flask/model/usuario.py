from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, UniqueConstraint, func, or_, update
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin

from model.database import Base, get_db
from model.role import Role

from utils.pbkdf import Pbkdf

class Usuario(Base, UserMixin):
    __tablename__ = 'Usuario'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_role : Mapped[int] = mapped_column(ForeignKey('Role.id'))
    username : Mapped[str] = mapped_column(String(120), nullable=False)
    nome_completo : Mapped[str] = mapped_column(Text, nullable=False)
    email : Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    pfp_url : Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    datahora_registro : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.current_timestamp())
    status : Mapped[str] = mapped_column(String(50), nullable=False, default="Ativo")
    key : Mapped[str] = mapped_column(Text, nullable=False)
    salt : Mapped[str] = mapped_column(Text, nullable=False)

    role : Mapped['Role'] = relationship(
        back_populates='usuarios', lazy='subquery'
    )

    __table_args__ = (
        UniqueConstraint("username", name="uq_username"),
    )

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

    def update(self, data):
        db = get_db()

        username = data['username'] if 'username' in data else self.username
        nome_completo = data['nome_completo'] if 'nome_completo' in data else self.nome_completo
        email = data['email'] if 'email' in data else self.email
        pfp_url = data['pfp_url'] if 'pfp_url' in data else self.pfp_url

        if 'new_password' in data and data['new_password']:
            key, salt = Pbkdf.hash_password(data['new_password'])
        else:
            key, salt = self.key, self.salt

        stmt = (
            update(Usuario)
            .where(Usuario.username == self.username)
            .values(
                username=username,
                nome_completo=nome_completo,
                email=email,
                pfp_url=pfp_url,
                key=key,
                salt=salt
            )
        )

        try:
            db.execute(stmt)
            db.commit()
            db.flush()
        except IntegrityError as e:
            db.rollback()
            raise e
        finally:
            db.remove()
            
    
    @staticmethod
    def get_all_usuarios():
        db = get_db()
        users = [
            user for user in db.query(Usuario, Role).filter(Usuario.id_role == Role.id).filter(Usuario.username != 'admin').all()
        ]
        db.remove()
        return users
    
    @staticmethod
    def get_usuario_by_id(id: str):
        db = get_db()
        user = db.query(Usuario).filter_by(id=id).first()
        db.remove()
        return user if user else None
    
    @staticmethod
    def get_usuario_by_username(username: str):
        db = get_db()
        user = db.query(Usuario).filter_by(username=username).first()
        db.remove()
        return user if user else None
    
    @staticmethod
    def get_usuario_by_email(email: str):
        db = get_db()
        user = db.query(Usuario).filter_by(email=email).first()
        db.remove()
        return user if user else None

    @staticmethod
    def get_usuario_by_username_or_email(username_or_email: str):
        db = get_db()
        usuario = db.query(Usuario).filter(or_(Usuario.username == username_or_email, Usuario.email == username_or_email)).first()
        db.remove()
        return usuario if usuario else None
    
    @staticmethod
    def ban_user_by_username(username: str):
        db = get_db()

        user = db.query(Usuario).filter_by(username=username).first()

        if not user:
            return None

        stmt = ()

        if (user.status == 'Ativo'):
            stmt = (
                update(Usuario)
                .where(Usuario.username == username)
                .values(status='Banido')
            )
        else:
            stmt = (
                update(Usuario)
                .where(Usuario.username == username)
                .values(status='Ativo')
            )

        db.execute(stmt)
        db.commit()
        db_user = db.query(Usuario).filter_by(username=username).first()
        db.remove()
        return db_user
    
    @staticmethod
    def delete_user_by_username(username: str):
        db = get_db()

        rows_affected = db.query(Usuario).filter(Usuario.username == username).delete()

        res = {
            'rowsAffected': rows_affected
        }
    
        db.commit()
        db.remove()
        return res
    
    @staticmethod
    def create_user(username: str, nome_completo: str, email: str, password: str, role: Role, pfp_url = None):
        db = get_db()
        
        key, salt = Pbkdf.hash_password(password)

        usuario = Usuario(
            id_role=role.id,
            username=username,
            nome_completo=nome_completo,
            email=email,
            salt=salt, key=key,
            pfp_url=pfp_url
        )

        try:
            db.add(usuario)
            db.commit()
            db.flush()
            return usuario
        except IntegrityError as e:
            db.rollback()
            raise e
        finally:
            db.remove()
    