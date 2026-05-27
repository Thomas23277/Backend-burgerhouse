from typing import List
from fastapi import HTTPException, status
from app.models import Usuario
from app.direcciones.schemas import DireccionCreate, DireccionUpdate, DireccionResponse
from app.direcciones.repository import DireccionRepository
from app.core import UnitOfWork


def _build_response(direccion) -> DireccionResponse:
    return DireccionResponse(
        id=direccion.id,
        usuario_id=direccion.usuario_id,
        alias=direccion.alias,
        direccion=direccion.direccion,
        ciudad=direccion.ciudad,
        codigo_postal=direccion.codigo_postal,
        es_principal=direccion.es_principal,
    )


def _check_pertenencia(direccion, usuario: Usuario):
    """Verifica que la dirección pertenezca al usuario (o sea ADMIN)."""
    if usuario.rol.upper() != "ADMIN" and direccion.usuario_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirección no encontrada",
        )


def get_all(usuario: Usuario) -> List[DireccionResponse]:
    with UnitOfWork() as uow:
        repo = DireccionRepository(uow.session)
        if usuario.rol.upper() == "ADMIN":
            # Admin ve todas las direcciones activas
            from app.models import DireccionEntrega
            from sqlmodel import select
            query = select(DireccionEntrega).where(DireccionEntrega.deleted_at.is_(None))
            direcciones = list(uow.session.exec(query).all())
        else:
            direcciones = repo.get_all_by_usuario(usuario.id)
        return [_build_response(d) for d in direcciones]


def get_by_id(id: int, usuario: Usuario) -> DireccionResponse:
    with UnitOfWork() as uow:
        repo = DireccionRepository(uow.session)
        direccion = repo.get_by_id(id)
        if not direccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dirección no encontrada",
            )
        _check_pertenencia(direccion, usuario)
        return _build_response(direccion)


def create(data: DireccionCreate, usuario: Usuario) -> DireccionResponse:
    with UnitOfWork() as uow:
        repo = DireccionRepository(uow.session)

        # Si es la primera dirección, marcar como principal automáticamente
        existing = repo.get_all_by_usuario(usuario.id)
        if len(existing) == 0:
            data.es_principal = True

        # Si se marca como principal, desmarcar las demás
        if data.es_principal:
            repo.unset_principal_for_usuario(usuario.id)

        direccion = repo.create(data, usuario.id)
        return _build_response(direccion)


def update(id: int, data: DireccionUpdate, usuario: Usuario) -> DireccionResponse:
    with UnitOfWork() as uow:
        repo = DireccionRepository(uow.session)
        direccion = repo.get_by_id(id)
        if not direccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dirección no encontrada",
            )
        _check_pertenencia(direccion, usuario)

        # Si se marca como principal, desmarcar las demás
        if data.es_principal:
            repo.unset_principal_for_usuario(usuario.id)

        direccion = repo.update(id, data)
        return _build_response(direccion)


def set_principal(id: int, usuario: Usuario) -> DireccionResponse:
    with UnitOfWork() as uow:
        repo = DireccionRepository(uow.session)
        direccion = repo.get_by_id(id)
        if not direccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dirección no encontrada",
            )
        _check_pertenencia(direccion, usuario)

        # Desmarcar todas y marcar esta
        repo.unset_principal_for_usuario(usuario.id)
        direccion.es_principal = True
        uow.session.flush()

        return _build_response(direccion)


def delete(id: int, usuario: Usuario) -> dict:
    with UnitOfWork() as uow:
        repo = DireccionRepository(uow.session)
        direccion = repo.get_by_id(id)
        if not direccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dirección no encontrada",
            )
        _check_pertenencia(direccion, usuario)

        repo.soft_delete(id)
        return {"message": "Dirección eliminada correctamente", "type": "soft_delete"}
