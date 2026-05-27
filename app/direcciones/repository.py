from typing import Optional, List
from sqlmodel import Session, select
from app.models import DireccionEntrega
from datetime import datetime


class DireccionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_by_usuario(self, usuario_id: int) -> List[DireccionEntrega]:
        query = (
            select(DireccionEntrega)
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.deleted_at.is_(None))
        )
        return list(self.session.exec(query).all())

    def get_by_id(self, id: int) -> Optional[DireccionEntrega]:
        direccion = self.session.get(DireccionEntrega, id)
        if direccion and direccion.deleted_at is not None:
            return None
        return direccion

    def create(self, data: "DireccionCreate", usuario_id: int) -> DireccionEntrega:
        direccion = DireccionEntrega(
            **data.model_dump(),
            usuario_id=usuario_id,
        )
        self.session.add(direccion)
        self.session.flush()
        return direccion

    def update(
        self, id: int, data: "DireccionUpdate"
    ) -> Optional[DireccionEntrega]:
        direccion = self.get_by_id(id)
        if not direccion:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(direccion, key, value)
        self.session.flush()
        return direccion

    def soft_delete(self, id: int) -> Optional[DireccionEntrega]:
        direccion = self.get_by_id(id)
        if not direccion:
            return None
        direccion.deleted_at = datetime.now()
        self.session.flush()
        return direccion

    def unset_principal_for_usuario(self, usuario_id: int):
        """Desmarca todas las direcciones del usuario como no principal."""
        query = (
            select(DireccionEntrega)
            .where(DireccionEntrega.usuario_id == usuario_id)
            .where(DireccionEntrega.es_principal == True)
            .where(DireccionEntrega.deleted_at.is_(None))
        )
        direcciones = self.session.exec(query).all()
        for d in direcciones:
            d.es_principal = False
        self.session.flush()
