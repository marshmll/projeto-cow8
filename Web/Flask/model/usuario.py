from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, DateTime, UniqueConstraint, func, or_, update
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin
import bcrypt
from base64 import b64encode

from .base import Base
from model.database import get_db
from utils.pbkdf import Pbkdf

class Usuario(Base, UserMixin):
    __tablename__ = 'Usuario'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username : Mapped[str] = mapped_column(String(120), nullable=False)
    nome_completo : Mapped[str] = mapped_column(Text, nullable=False)
    email : Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    pfp_url : Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    datahora_registro : Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.current_timestamp())
    status : Mapped[str] = mapped_column(String(50), nullable=False, default="Ativo")
    privilegios : Mapped[str] = mapped_column(String(50), nullable=False, default="Usuário")
    key : Mapped[str] = mapped_column(Text, nullable=False)
    salt : Mapped[str] = mapped_column(Text, nullable=False)

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

        # Update non-password fields
        if 'username' in data:
            self.username = data['username']
        if 'nome_completo' in data:
            self.nome_completo = data['nome_completo']
        if 'email' in data:
            self.email = data['email']
        if 'pfp_url' in data:
            self.pfp_url = data['pfp_url']

        # Update password (if provided)
        if 'new_password' in data and data['new_password']:
            salt = bcrypt.gensalt(rounds=12)
            salt_str = b64encode(salt).decode('utf-8')
            key = bcrypt.kdf(
                password=data['new_password'].encode(),
                salt=salt,
                desired_key_bytes=32,
                rounds=100
            )
            key_str = b64encode(key).decode('utf-8')
            self.key = key_str
            self.salt = salt_str

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise e
        finally:
            db.remove()
            
    
    @staticmethod
    def get_all_usuarios():
        db = get_db()
        users = [user for user in db.query(Usuario).filter(Usuario.username != 'admin').all()]
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
    def create_user(username: str, nome_completo: str, email: str, password: str, privilegios: str = "Usuário", pfp_url = None):
        db = get_db()
        
        key, salt = Pbkdf.hash_password(password)

        usuario = Usuario(
            username=username,
            nome_completo=nome_completo,
            email=email,
            privilegios=privilegios,
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
    