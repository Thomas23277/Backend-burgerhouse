from typing import Optional, List
from sqlmodel import Session, select
from app.models import Pedido, PedidoDetalle, HistorialEstadoPedido
from datetime import datetime


class PedidoRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Pedido]:
        query = select(Pedido).where(Pedido.deleted_at.is_(None))
        return list(self.session.exec(query).all())

    def get_by_id(self, id: int) -> Optional[Pedido]:
        pedido = self.session.get(Pedido, id)
        if pedido and pedido.deleted_at is not None:
            return None
        return pedido

    def create(self, usuario_id: int, total: float, notas: Optional[str]) -> Pedido:
        pedido = Pedido(usuario_id=usuario_id, total=total, notas=notas)
        self.session.add(pedido)
        self.session.flush()
        return pedido

    def add_detalle(self, pedido_id: int, producto_id: int, cantidad: int,
                    precio_unitario: float, nombre_producto: str, notas: Optional[str]) -> PedidoDetalle:
        detalle = PedidoDetalle(
            pedido_id=pedido_id, producto_id=producto_id, cantidad=cantidad,
            precio_unitario=precio_unitario, nombre_producto=nombre_producto, notas=notas,
        )
        self.session.add(detalle)
        self.session.flush()
        return detalle

    def create_historial(self, pedido_id: int, estado_anterior: Optional[str],
                         estado_nuevo: str, cambiado_por: int) -> HistorialEstadoPedido:
        registro = HistorialEstadoPedido(
            pedido_id=pedido_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            cambiado_por=cambiado_por,
        )
        self.session.add(registro)
        self.session.flush()
        return registro

    def get_historial(self, pedido_id: int) -> List[HistorialEstadoPedido]:
        query = (
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at.asc())
        )
        return list(self.session.exec(query).all())

    def update(self, id: int, data: "PedidoUpdate") -> Optional[Pedido]:
        pedido = self.get_by_id(id)
        if not pedido:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(pedido, key, value)
        self.session.flush()
        return pedido

    def soft_delete(self, id: int) -> Optional[Pedido]:
        pedido = self.get_by_id(id)
        if not pedido:
            return None
        pedido.deleted_at = datetime.now()
        self.session.flush()
        return pedido
