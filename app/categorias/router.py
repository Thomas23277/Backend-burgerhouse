from fastapi import APIRouter, status, Depends
from typing import List
from app.models import Usuario
from app.categorias.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.core.dependencies import require_roles
import app.categorias.service as service

router = APIRouter()


@router.get("/categorias", response_model=List[CategoriaResponse])
def get_categorias():
    """Público: listado de categorías activas."""
    return service.get_all()


@router.get("/categorias/{id}", response_model=CategoriaResponse)
def get_categoria(id: int):
    """Público: detalle de categoría."""
    return service.get_by_id(id)


@router.post(
    "/categorias",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_categoria(
    data: CategoriaCreate,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: crear categoría."""
    return service.create(data)


@router.put("/categorias/{id}", response_model=CategoriaResponse)
def update_categoria(
    id: int,
    data: CategoriaUpdate,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: actualizar categoría."""
    return service.update(id, data)


@router.delete("/categorias/{id}")
def delete_categoria(
    id: int,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: eliminar categoría."""
    return service.delete(id)
