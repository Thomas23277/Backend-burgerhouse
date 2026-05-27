from typing import List, Optional
from fastapi import HTTPException, status
from app.pedidos.schemas import (
    PedidoCreate, PedidoUpdate, PedidoResponse, PedidoDetalleResponse, HistorialResponse
)
from app.pedidos.repository import PedidoRepository
from app.productos.repository import ProductoRepository
from app.usuarios.repository import UsuarioRepository
from app.core import UnitOfWork

# ──────────────────────────────────────────────
# Máquina de Estados
# ──────────────────────────────────────────────

ESTADOS = {
    "pendiente": "Pendiente",
    "confirmado": "Confirmado",
    "en_prep": "En Preparación",
    "en_camino": "En Camino",
    "entregado": "Entregado",
    "cancelado": "Cancelado",
}

TRANSICIONES_VALIDAS = {
    "pendiente": ["confirmado", "cancelado"],
    "confirmado": ["en_prep", "cancelado"],
    "en_prep": ["en_camino", "cancelado"],
    "en_camino": ["entregado"],
    "entregado": [],        # estado final
    "cancelado": [],        # estado final
}


def _validar_transicion(estado_actual: str, estado_nuevo: str) -> None:
    """Valida que la transición sea permitida por la máquina de estados."""
    if estado_actual not in TRANSICIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado '{estado_actual}' no es válido",
        )
    if estado_nuevo not in ESTADOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado '{estado_nuevo}' no es válido. Válidos: {', '.join(ESTADOS.keys())}",
        )
    if estado_nuevo not in TRANSICIONES_VALIDAS[estado_actual]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Transición inválida: de '{estado_actual}' a '{estado_nuevo}'. "
                f"Transiciones permitidas: {', '.join(TRANSICIONES_VALIDAS[estado_actual]) or 'ninguna (estado final)'}"
            ),
        )


def _build_response(pedido) -> PedidoResponse:
    detalles = []
    if pedido.detalles:
        for d in pedido.detalles:
            detalles.append(PedidoDetalleResponse(
                id=d.id, producto_id=d.producto_id, cantidad=d.cantidad,
                precio_unitario=d.precio_unitario, nombre_producto=d.nombre_producto,
                notas=d.notas,
            ))
    return PedidoResponse(
        id=pedido.id, usuario_id=pedido.usuario_id, estado=pedido.estado,
        total=pedido.total, notas=pedido.notas, created_at=pedido.created_at,
        updated_at=pedido.updated_at, detalles=detalles,
    )


def get_all() -> List[PedidoResponse]:
    with UnitOfWork() as uow:
        repo = PedidoRepository(uow.session)
        pedidos = repo.get_all()
        return [_build_response(p) for p in pedidos]


def get_by_id(id: int) -> PedidoResponse:
    with UnitOfWork() as uow:
        repo = PedidoRepository(uow.session)
        pedido = repo.get_by_id(id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return _build_response(pedido)


def get_by_usuario(usuario_id: int) -> List[PedidoResponse]:
    """Retorna los pedidos de un usuario específico."""
    with UnitOfWork() as uow:
        repo = PedidoRepository(uow.session)
        pedidos = repo.get_all()
        # Filtrar por usuario_id en memoria (los pedidos ya vienen sin soft-delete del repo)
        pedidos_usuario = [p for p in pedidos if p.usuario_id == usuario_id]
        return [_build_response(p) for p in pedidos_usuario]


def create(data: PedidoCreate, usuario_id_actual: int) -> PedidoResponse:
    with UnitOfWork() as uow:
        usuario_repo = UsuarioRepository(uow.session)
        usuario = usuario_repo.get_by_id(data.usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        producto_repo = ProductoRepository(uow.session)

        total = 0.0
        for detalle in data.detalles:
            producto = producto_repo.get_by_id(detalle.producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail=f"Producto {detalle.producto_id} no encontrado")
            total += producto.precio_base * detalle.cantidad

        pedido_repo = PedidoRepository(uow.session)
        pedido = pedido_repo.create(
            usuario_id=data.usuario_id, total=total, notas=data.notas,
        )

        for detalle in data.detalles:
            producto = producto_repo.get_by_id(detalle.producto_id)
            pedido_repo.add_detalle(
                pedido_id=pedido.id, producto_id=detalle.producto_id,
                cantidad=detalle.cantidad, precio_unitario=producto.precio_base,
                nombre_producto=producto.nombre, notas=detalle.notas,
            )

        # Registrar estado inicial en historial
        pedido_repo.create_historial(
            pedido_id=pedido.id,
            estado_anterior=None,
            estado_nuevo="pendiente",
            cambiado_por=usuario_id_actual,
        )

        uow.session.refresh(pedido)
        _ = pedido.detalles
        _ = pedido.historial
        return _build_response(pedido)


def update(id: int, data: PedidoUpdate, usuario_id_actual: int) -> PedidoResponse:
    with UnitOfWork() as uow:
        repo = PedidoRepository(uow.session)
        pedido = repo.get_by_id(id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        estado_anterior = pedido.estado

        # Si se está cambiando el estado, validar transición
        if data.estado is not None and data.estado != estado_anterior:
            _validar_transicion(estado_anterior, data.estado)

        # Guardar notas si vienen
        if data.notas is not None:
            pedido.notas = data.notas

        # Actualizar estado si viene
        estado_nuevo = estado_anterior
        if data.estado is not None and data.estado != estado_anterior:
            pedido.estado = data.estado
            estado_nuevo = data.estado
            repo.create_historial(
                pedido_id=id,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
                cambiado_por=usuario_id_actual,
            )

        repo.session.flush()
        return _build_response(pedido)


def get_historial(id: int) -> List[HistorialResponse]:
    with UnitOfWork() as uow:
        repo = PedidoRepository(uow.session)
        pedido = repo.get_by_id(id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        registros = repo.get_historial(id)
        return [
            HistorialResponse(
                id=r.id,
                estado_anterior=r.estado_anterior,
                estado_nuevo=r.estado_nuevo,
                cambiado_por=r.cambiado_por,
                created_at=r.created_at,
            )
            for r in registros
        ]
