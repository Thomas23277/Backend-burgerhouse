from fastapi import APIRouter, status, Depends
from typing import List
from app.models import Usuario
from app.direcciones.schemas import DireccionCreate, DireccionUpdate, DireccionResponse
from app.core.dependencies import get_current_user
import app.direcciones.service as service

router = APIRouter()


@router.get("/direcciones", response_model=List[DireccionResponse])
def get_direcciones(usuario: Usuario = Depends(get_current_user)):
    """Listar direcciones del usuario autenticado."""
    return service.get_all(usuario)


@router.get("/direcciones/{id}", response_model=DireccionResponse)
def get_direccion(id: int, usuario: Usuario = Depends(get_current_user)):
    """Obtener detalle de una dirección (solo propia)."""
    return service.get_by_id(id, usuario)


@router.post(
    "/direcciones",
    response_model=DireccionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_direccion(
    data: DireccionCreate,
    usuario: Usuario = Depends(get_current_user),
):
    """Crear una nueva dirección."""
    return service.create(data, usuario)


@router.put("/direcciones/{id}", response_model=DireccionResponse)
def update_direccion(
    id: int,
    data: DireccionUpdate,
    usuario: Usuario = Depends(get_current_user),
):
    """Actualizar una dirección existente."""
    return service.update(id, data, usuario)


@router.patch("/direcciones/{id}/principal", response_model=DireccionResponse)
def set_direccion_principal(
    id: int,
    usuario: Usuario = Depends(get_current_user),
):
    """Marcar una dirección como principal."""
    return service.set_principal(id, usuario)


@router.delete("/direcciones/{id}")
def delete_direccion(
    id: int,
    usuario: Usuario = Depends(get_current_user),
):
    """Eliminar (soft delete) una dirección."""
    return service.delete(id, usuario)
