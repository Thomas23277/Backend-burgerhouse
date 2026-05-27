from typing import List
from fastapi import HTTPException
from sqlmodel import select
from app.models import Categoria, Producto, ProductoCategoria
from app.categorias.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.categorias.repository import CategoriaRepository
from app.core import UnitOfWork
from datetime import datetime


def _build_response(categoria: Categoria) -> CategoriaResponse:
    subcategorias = []
    if categoria.children:
        subcategorias = [
            _build_response(h) for h in categoria.children
            if h.deleted_at is None
        ]
    return CategoriaResponse(
        id=categoria.id,
        nombre=categoria.nombre,
        descripcion=categoria.descripcion,
        imagen_url=categoria.imagen_url,
        parent_id=categoria.parent_id,
        es_activa=categoria.es_activa,
        subcategorias=subcategorias,
    )


def get_all() -> List[CategoriaResponse]:
    with UnitOfWork() as uow:
        repo = CategoriaRepository(uow.session)
        categorias = repo.get_all()
        raices = [c for c in categorias if c.parent_id is None]
        return [_build_response(c) for c in raices]


def get_by_id(id: int) -> CategoriaResponse:
    with UnitOfWork() as uow:
        repo = CategoriaRepository(uow.session)
        categoria = repo.get_by_id(id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return _build_response(categoria)


def create(data: CategoriaCreate) -> CategoriaResponse:
    with UnitOfWork() as uow:
        repo = CategoriaRepository(uow.session)
        categoria = repo.create(data)
        return _build_response(categoria)


def update(id: int, data: CategoriaUpdate) -> CategoriaResponse:
    with UnitOfWork() as uow:
        repo = CategoriaRepository(uow.session)
        categoria = repo.update(id, data)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return _build_response(categoria)


def delete(id: int) -> dict:
    with UnitOfWork() as uow:
        repo = CategoriaRepository(uow.session)
        categoria = repo.get_by_id(id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        # Verificar si la categoría (o sus subcategorías) tienen productos activos (no soft-deleted)
        categorias_a_verificar = [categoria.id]
        if categoria.children:
            categorias_a_verificar.extend(c.id for c in categoria.children)

        productos_activos = uow.session.exec(
            select(ProductoCategoria)
            .join(Producto, ProductoCategoria.producto_id == Producto.id)
            .where(
                ProductoCategoria.categoria_id.in_(categorias_a_verificar),
                Producto.deleted_at.is_(None),
            )
        ).all()

        if len(productos_activos) > 0:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar la categoría porque tiene productos activos asociados. "
                       "Desasocie o elimine los productos primero."
            )

        now = datetime.now()
        # Soft-delete también subcategorías
        for child in categoria.children:
            child.deleted_at = now

        repo.soft_delete(id)
        return {"message": "Categoría eliminada correctamente", "type": "soft_delete"}
