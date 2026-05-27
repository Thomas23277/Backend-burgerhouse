from typing import Optional, List
from sqlmodel import Session, select
from app.models import Usuario
from datetime import datetime


class UsuarioRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Usuario]:
        query = select(Usuario).where(Usuario.deleted_at.is_(None))
        return list(self.session.exec(query).all())

    def get_by_id(self, id: int) -> Optional[Usuario]:
        usuario = self.session.get(Usuario, id)
        if usuario and usuario.deleted_at is not None:
            return None
        return usuario

    def get_by_username(self, username: str) -> Optional[Usuario]:
        return self.session.exec(
            select(Usuario).where(Usuario.username == username, Usuario.deleted_at.is_(None))
        ).first()

    def create(self, username: str, email: str, nombre: str, rol: str, hashed_password: str) -> Usuario:
        usuario = Usuario(
            username=username, email=email, nombre=nombre,
            rol=rol, hashed_password=hashed_password,
        )
        self.session.add(usuario)
        self.session.flush()
        return usuario

    def soft_delete(self, id: int) -> Optional[Usuario]:
        usuario = self.get_by_id(id)
        if not usuario:
            return None
        usuario.deleted_at = datetime.now()
        self.session.flush()
        return usuario
