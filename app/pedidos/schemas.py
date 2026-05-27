from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class PedidoDetalleCreate(BaseModel):
    producto_id: int
    cantidad: int = 1
    notas: Optional[str] = None


class PedidoDetalleResponse(PedidoDetalleCreate):
    id: int
    precio_unitario: float
    nombre_producto: str

    class Config:
        from_attributes = True


class PedidoBase(BaseModel):
    notas: Optional[str] = None


class PedidoCreate(PedidoBase):
    usuario_id: int
    detalles: List[PedidoDetalleCreate] = []


class PedidoUpdate(BaseModel):
    estado: Optional[str] = None
    notas: Optional[str] = None


class HistorialResponse(BaseModel):
    id: int
    estado_anterior: Optional[str] = None
    estado_nuevo: str
    cambiado_por: int
    created_at: datetime

    class Config:
        from_attributes = True


class PedidoResponse(PedidoBase):
    id: int
    usuario_id: int
    estado: str
    total: float
    created_at: datetime
    updated_at: datetime
    detalles: List[PedidoDetalleResponse] = []

    class Config:
        from_attributes = True
