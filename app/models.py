from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="categorias.id")
    es_activa: bool = Field(default=True)
    deleted_at: Optional[datetime] = Field(default=None)

    parent: Optional["Categoria"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Categoria.id"}
    )
    children: List["Categoria"] = Relationship(back_populates="parent")
    productos: List["ProductoCategoria"] = Relationship(back_populates="categoria")


class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingredientes"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    precio_adicional: float = Field(default=0.0)
    imagen_url: Optional[str] = None
    disponible: bool = Field(default=True)
    deleted_at: Optional[datetime] = Field(default=None)

    productos: List["ProductoIngrediente"] = Relationship(back_populates="ingrediente")


class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=200)
    descripcion: Optional[str] = None
    precio_base: float
    imagenes_url: Optional[str] = None
    stock_cantidad: int = Field(default=0)
    disponible: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = Field(default=None)

    categorias: List["ProductoCategoria"] = Relationship(back_populates="producto")
    ingredientes: List["ProductoIngrediente"] = Relationship(back_populates="producto")


class ProductoCategoria(SQLModel, table=True):
    __tablename__ = "producto_categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    producto_id: int = Field(foreign_key="productos.id")
    categoria_id: int = Field(foreign_key="categorias.id")
    es_principal: bool = Field(default=False)

    producto: "Producto" = Relationship(back_populates="categorias")
    categoria: "Categoria" = Relationship(back_populates="productos")


class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingredientes"

    id: Optional[int] = Field(default=None, primary_key=True)
    producto_id: int = Field(foreign_key="productos.id")
    ingrediente_id: int = Field(foreign_key="ingredientes.id")
    es_removible: bool = Field(default=False)
    es_alergeno: bool = Field(default=False)

    producto: "Producto" = Relationship(back_populates="ingredientes")
    ingrediente: "Ingrediente" = Relationship(back_populates="productos")


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=100, unique=True)
    email: str = Field(max_length=200, unique=True)
    hashed_password: str
    nombre: str
    rol: str = Field(default="cliente")
    created_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = Field(default=None)


class Pedido(SQLModel, table=True):
    __tablename__ = "pedidos"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    estado: str = Field(default="pendiente")
    total: float = Field(default=0.0)
    notas: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = Field(default=None)

    detalles: List["PedidoDetalle"] = Relationship(back_populates="pedido")
    historial: List["HistorialEstadoPedido"] = Relationship(back_populates="pedido")


class Rol(SQLModel, table=True):
    """Catálogo de roles del sistema."""
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(max_length=20, unique=True)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None


class EstadoPedido(SQLModel, table=True):
    """Catálogo de estados posibles para un pedido."""
    __tablename__ = "estados_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(max_length=20, unique=True)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None


class FormaPago(SQLModel, table=True):
    """Catálogo de formas de pago."""
    __tablename__ = "formas_pago"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(max_length=20, unique=True)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None


class DireccionEntrega(SQLModel, table=True):
    """Direcciones de entrega por usuario."""
    __tablename__ = "direcciones"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    alias: str = Field(max_length=50)
    direccion: str = Field(max_length=255)
    ciudad: str = Field(max_length=100)
    codigo_postal: str = Field(max_length=20)
    es_principal: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)


class HistorialEstadoPedido(SQLModel, table=True):
    """Registro de cambios de estado de un pedido (audit trail)."""
    __tablename__ = "historial_estados"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id")
    estado_anterior: Optional[str] = Field(default=None, max_length=20)
    estado_nuevo: str = Field(max_length=20)
    cambiado_por: int = Field(foreign_key="usuarios.id")
    created_at: datetime = Field(default_factory=datetime.now)

    pedido: Optional["Pedido"] = Relationship(back_populates="historial")


class PedidoDetalle(SQLModel, table=True):
    __tablename__ = "pedido_detalles"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id")
    producto_id: int = Field(foreign_key="productos.id")
    cantidad: int = Field(default=1)
    precio_unitario: float
    nombre_producto: str = Field(max_length=200)
    notas: Optional[str] = None

    pedido: Optional["Pedido"] = Relationship(back_populates="detalles")