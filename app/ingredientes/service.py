from typing import List
from fastapi import HTTPException
from app.models import Ingrediente
from app.ingredientes.schemas import IngredienteCreate, IngredienteUpdate, IngredienteResponse
from app.ingredientes.repository import IngredienteRepository
from app.core import UnitOfWork


def _build_response(ingrediente: Ingrediente) -> IngredienteResponse:
    return IngredienteResponse(
        id=ingrediente.id,
        nombre=ingrediente.nombre,
        descripcion=ingrediente.descripcion,
        precio_adicional=ingrediente.precio_adicional,
        imagen_url=ingrediente.imagen_url,
        disponible=ingrediente.disponible,
        alergeno=ingrediente.alergeno,
    )


def get_all() -> List[IngredienteResponse]:
    with UnitOfWork() as uow:
        repo = IngredienteRepository(uow.session)
        ingredientes = repo.get_all()
        return [_build_response(i) for i in ingredientes]


def get_by_id(id: int) -> IngredienteResponse:
    with UnitOfWork() as uow:
        repo = IngredienteRepository(uow.session)
        ingrediente = repo.get_by_id(id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return _build_response(ingrediente)


def create(data: IngredienteCreate) -> IngredienteResponse:
    with UnitOfWork() as uow:
        repo = IngredienteRepository(uow.session)
        ingrediente = repo.create(data)
        return _build_response(ingrediente)


def update(id: int, data: IngredienteUpdate) -> IngredienteResponse:
    with UnitOfWork() as uow:
        repo = IngredienteRepository(uow.session)
        ingrediente = repo.update(id, data)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return _build_response(ingrediente)


def delete(id: int) -> dict:
    with UnitOfWork() as uow:
        repo = IngredienteRepository(uow.session)
        ingrediente = repo.soft_delete(id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return {"message": "Ingrediente eliminado correctamente", "type": "soft_delete"}
