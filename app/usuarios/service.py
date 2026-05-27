from typing import List
from fastapi import HTTPException, status
from app.models import Usuario
from app.usuarios.schemas import UsuarioCreate, UsuarioResponse
from app.usuarios.repository import UsuarioRepository
from app.core import UnitOfWork
from app.core.security import hash_password


def get_all() -> List[UsuarioResponse]:
    with UnitOfWork() as uow:
        repo = UsuarioRepository(uow.session)
        usuarios = repo.get_all()
        return [UsuarioResponse(
            id=u.id, username=u.username, email=u.email,
            nombre=u.nombre, rol=u.rol, created_at=u.created_at
        ) for u in usuarios]


def get_by_id(id: int) -> UsuarioResponse:
    with UnitOfWork() as uow:
        repo = UsuarioRepository(uow.session)
        usuario = repo.get_by_id(id)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return UsuarioResponse(
            id=usuario.id, username=usuario.username, email=usuario.email,
            nombre=usuario.nombre, rol=usuario.rol, created_at=usuario.created_at,
        )


def create(data: UsuarioCreate) -> UsuarioResponse:
    with UnitOfWork() as uow:
        repo = UsuarioRepository(uow.session)
        existing = repo.get_by_username(data.username)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El username ya existe")
        hashed_password = hash_password(data.password)
        usuario = repo.create(
            username=data.username, email=data.email,
            nombre=data.nombre, rol=data.rol,
            hashed_password=hashed_password,
        )
        return UsuarioResponse(
            id=usuario.id, username=usuario.username, email=usuario.email,
            nombre=usuario.nombre, rol=usuario.rol, created_at=usuario.created_at,
        )
