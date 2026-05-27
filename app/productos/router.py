from fastapi import APIRouter, status, Depends, Query
from typing import List, Optional
from app.models import Usuario
from app.productos.schemas import ProductoCreate, ProductoUpdate, ProductoResponse
from app.core.dependencies import require_roles
import app.productos.service as service

router = APIRouter()


@router.get("/productos/destacados", response_model=List[ProductoResponse])
def get_productos_destacados(
    limite: int = Query(6, ge=1, le=20, description="Cantidad de productos a devolver"),
):
    """Público: productos destacados para la store home."""
    return service.get_destacados(limite=limite)


@router.get("/productos", response_model=List[ProductoResponse])
def get_productos(
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima por página"),
    offset: int = Query(0, ge=0, description="Desplazamiento"),
):
    """Público: listado de productos con filtros opcionales y paginación."""
    return service.get_all(
        categoria_id=categoria_id,
        search=search,
        disponible=disponible,
        limit=limit,
        offset=offset,
    )


@router.get("/productos/{id}", response_model=ProductoResponse)
def get_producto(id: int):
    """Público: detalle de producto."""
    return service.get_by_id(id)


@router.post(
    "/productos",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_producto(
    data: ProductoCreate,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: crear producto."""
    return service.create(data)


@router.put("/productos/{id}", response_model=ProductoResponse)
def update_producto(
    id: int,
    data: ProductoUpdate,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: actualizar producto."""
    return service.update(id, data)


@router.patch("/productos/{id}/disponibilidad", response_model=ProductoResponse)
def toggle_disponibilidad(
    id: int,
    usuario: Usuario = Depends(require_roles("ADMIN", "STOCK")),
):
    """ADMIN o STOCK: activar/desactivar disponibilidad de un producto."""
    return service.toggle_disponibilidad(id)


@router.delete("/productos/{id}")
def delete_producto(
    id: int,
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    """Solo ADMIN: eliminar producto."""
    return service.delete(id)
