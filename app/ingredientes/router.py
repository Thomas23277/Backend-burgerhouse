from fastapi import APIRouter, status, Depends
from typing import List
from app.models import Usuario
from app.ingredientes.schemas import IngredienteCreate, IngredienteUpdate, IngredienteResponse
from app.core.dependencies import require_roles
import app.ingredientes.service as service

router = APIRouter()


@router.get("/ingredientes", response_model=List[IngredienteResponse])
def get_ingredientes():
    """Público: listado de ingredientes."""
    return service.get_all()


@router.get("/ingredientes/{id}", response_model=IngredienteResponse)
def get_ingrediente(id: int):
    """Público: detalle de ingrediente."""
    return service.get_by_id(id)


@router.post(
    "/ingredientes",
    response_model=IngredienteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ingrediente(
    data: IngredienteCreate,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: crear ingrediente."""
    return service.create(data)


@router.put("/ingredientes/{id}", response_model=IngredienteResponse)
def update_ingrediente(
    id: int,
    data: IngredienteUpdate,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: actualizar ingrediente."""
    return service.update(id, data)


@router.delete("/ingredientes/{id}")
def delete_ingrediente(
    id: int,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: eliminar ingrediente."""
    return service.delete(id)
