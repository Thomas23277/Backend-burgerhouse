from typing import List
from fastapi import APIRouter, status, Depends
from app.models import Usuario
from app.pedidos.schemas import PedidoCreate, PedidoUpdate, PedidoResponse, HistorialResponse
from app.core.dependencies import get_current_user, require_roles
import app.pedidos.service as service

router = APIRouter()


@router.get("/pedidos", response_model=List[PedidoResponse])
def get_pedidos(
    usuario: Usuario = Depends(require_roles("ADMIN", "PEDIDOS")),
):
    """Solo ADMIN/PEDIDOS: listado de todos los pedidos."""
    return service.get_all()


@router.get("/pedidos/mios", response_model=List[PedidoResponse])
def get_mis_pedidos(
    usuario: Usuario = Depends(get_current_user),
):
    """Usuario autenticado: sus propios pedidos."""
    return service.get_by_usuario(usuario.id)


@router.get("/pedidos/{id}/historial", response_model=List[HistorialResponse])
def get_historial_pedido(
    id: int,
    usuario: Usuario = Depends(get_current_user),
):
    """Autenticado: historial de cambios de estado de un pedido."""
    return service.get_historial(id)


@router.get("/pedidos/{id}", response_model=PedidoResponse)
def get_pedido(
    id: int,
    usuario: Usuario = Depends(require_roles("ADMIN", "PEDIDOS")),
):
    """Solo ADMIN/PEDIDOS: detalle de pedido."""
    return service.get_by_id(id)


@router.post(
    "/pedidos",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pedido(
    data: PedidoCreate,
    usuario: Usuario = Depends(get_current_user),
):
    """Requiere autenticación: crear pedido."""
    return service.create(data, usuario_id_actual=usuario.id)


@router.put("/pedidos/{id}", response_model=PedidoResponse)
def update_pedido(
    id: int,
    data: PedidoUpdate,
    usuario: Usuario = Depends(require_roles("ADMIN", "PEDIDOS")),
):
    """Solo ADMIN/PEDIDOS: actualizar estado de pedido."""
    return service.update(id, data, usuario_id_actual=usuario.id)
