from typing import List
from fastapi import APIRouter, status, Depends
from app.models import Usuario
from app.usuarios.schemas import UsuarioCreate, UsuarioResponse
from app.core.dependencies import require_roles
import app.usuarios.service as service

router = APIRouter()


@router.get("/usuarios", response_model=List[UsuarioResponse])
def get_usuarios(
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: listado de usuarios."""
    return service.get_all()


@router.get("/usuarios/{id}", response_model=UsuarioResponse)
def get_usuario(
    id: int,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: detalle de usuario."""
    return service.get_by_id(id)


@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(data: UsuarioCreate):
    """Público: registro de usuario (rol cliente por defecto)."""
    return service.create(data)
