from typing import List, Optional
from fastapi import HTTPException, status
from app.models import Producto, ProductoCategoria
from app.productos.schemas import (
    ProductoCreate, ProductoUpdate, ProductoResponse, CategoriaNested, IngredienteNested
)
from app.productos.repository import ProductoRepository
from app.categorias.repository import CategoriaRepository
from app.ingredientes.repository import IngredienteRepository
from app.core import UnitOfWork


def _build_response(producto: Producto) -> ProductoResponse:
    categorias = []
    if producto.categorias:
        for pc in producto.categorias:
            if pc.categoria:
                categorias.append(CategoriaNested(
                    id=pc.categoria.id, nombre=pc.categoria.nombre,
                    imagen_url=pc.categoria.imagen_url, es_principal=pc.es_principal
                ))

    ingredientes = []
    if producto.ingredientes:
        for pi in producto.ingredientes:
            if pi.ingrediente:
                ingredientes.append(IngredienteNested(
                    id=pi.ingrediente.id, nombre=pi.ingrediente.nombre,
                    precio_adicional=pi.ingrediente.precio_adicional,
                    imagen_url=pi.ingrediente.imagen_url,
                    es_alergeno=pi.es_alergeno,
                ))

    return ProductoResponse(
        id=producto.id, nombre=producto.nombre,
        descripcion=producto.descripcion, precio_base=producto.precio_base,
        imagenes_url=producto.imagenes_url, stock_cantidad=producto.stock_cantidad,
        disponible=producto.disponible, created_at=producto.created_at,
        updated_at=producto.updated_at, categorias=categorias, ingredientes=ingredientes,
    )


def get_all(
    categoria_id: Optional[int] = None,
    search: Optional[str] = None,
    disponible: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
) -> List[ProductoResponse]:
    with UnitOfWork() as uow:
        repo = ProductoRepository(uow.session)
        productos = repo.get_all(
            categoria_id=categoria_id,
            search=search,
            disponible=disponible,
            limit=limit,
            offset=offset,
        )
        return [_build_response(p) for p in productos]


def get_destacados(limite: int = 6) -> List[ProductoResponse]:
    with UnitOfWork() as uow:
        repo = ProductoRepository(uow.session)
        productos = repo.get_destacados(limite=limite)
        return [_build_response(p) for p in productos]


def get_by_id(id: int) -> ProductoResponse:
    with UnitOfWork() as uow:
        repo = ProductoRepository(uow.session)
        producto = repo.get_by_id(id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return _build_response(producto)


def create(data: ProductoCreate) -> ProductoResponse:
    with UnitOfWork() as uow:
        repo = ProductoRepository(uow.session)

        principales = [c for c in data.categorias if c.es_principal]
        if len(principales) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo puede haber una categoría principal por producto"
            )

        producto = repo.create(
            nombre=data.nombre, descripcion=data.descripcion,
            precio_base=data.precio_base, imagenes_url=data.imagenes_url,
            stock_cantidad=data.stock_cantidad, disponible=data.disponible,
        )

        cat_repo = CategoriaRepository(uow.session)
        for cat_input in data.categorias:
            cat = cat_repo.get_by_id(cat_input.categoria_id)
            if not cat:
                raise HTTPException(status_code=404, detail=f"Categoría {cat_input.categoria_id} no encontrada")
            repo.add_categoria(producto.id, cat_input.categoria_id, cat_input.es_principal)

        ing_repo = IngredienteRepository(uow.session)
        for ing_input in data.ingredientes:
            ing = ing_repo.get_by_id(ing_input.ingrediente_id)
            if not ing:
                raise HTTPException(status_code=404, detail=f"Ingrediente {ing_input.ingrediente_id} no encontrado")
            repo.add_ingrediente(producto.id, ing_input.ingrediente_id, ing_input.es_removible, ing_input.es_alergeno)

        uow.session.refresh(producto)
        _ = producto.categorias
        _ = producto.ingredientes
        return _build_response(producto)


def update(id: int, data: ProductoUpdate) -> ProductoResponse:
    with UnitOfWork() as uow:
        repo = ProductoRepository(uow.session)
        producto = repo.update(id, data)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return _build_response(producto)


def toggle_disponibilidad(id: int) -> ProductoResponse:
    """Activa/desactiva la disponibilidad de un producto."""
    with UnitOfWork() as uow:
        repo = ProductoRepository(uow.session)
        producto = repo.get_by_id(id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        producto.disponible = not producto.disponible
        uow.session.flush()
        uow.session.refresh(producto)
        _ = producto.categorias
        _ = producto.ingredientes
        return _build_response(producto)


def delete(id: int) -> dict:
    with UnitOfWork() as uow:
        repo = ProductoRepository(uow.session)
        producto = repo.soft_delete(id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"message": "Producto eliminado correctamente", "type": "soft_delete"}
