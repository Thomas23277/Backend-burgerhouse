from typing import Optional, List
from sqlmodel import Session, select
from app.models import Ingrediente
from datetime import datetime


class IngredienteRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Ingrediente]:
        query = select(Ingrediente).where(Ingrediente.deleted_at.is_(None))
        return list(self.session.exec(query).all())

    def get_by_id(self, id: int) -> Optional[Ingrediente]:
        ingrediente = self.session.get(Ingrediente, id)
        if ingrediente and ingrediente.deleted_at is not None:
            return None
        return ingrediente

    def create(self, data: "IngredienteCreate") -> Ingrediente:
        ingrediente = Ingrediente(**data.model_dump())
        self.session.add(ingrediente)
        self.session.flush()
        return ingrediente

    def update(self, id: int, data: "IngredienteUpdate") -> Optional[Ingrediente]:
        ingrediente = self.get_by_id(id)
        if not ingrediente:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(ingrediente, key, value)
        self.session.flush()
        return ingrediente

    def soft_delete(self, id: int) -> Optional[Ingrediente]:
        ingrediente = self.get_by_id(id)
        if not ingrediente:
            return None
        ingrediente.deleted_at = datetime.now()
        self.session.flush()
        return ingrediente
