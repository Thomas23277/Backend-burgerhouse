from typing import Optional, List
from sqlmodel import Session, select, or_
from app.models import Producto, ProductoCategoria, ProductoIngrediente
from datetime import datetime


class ProductoRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(
        self,
        categoria_id: Optional[int] = None,
        search: Optional[str] = None,
        disponible: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Producto]:
        query = select(Producto).where(Producto.deleted_at.is_(None))

        if categoria_id is not None:
            subq = (
                select(ProductoCategoria.producto_id)
                .where(ProductoCategoria.categoria_id == categoria_id)
            )
            query = query.where(Producto.id.in_(subq))

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(Producto.nombre.ilike(pattern), Producto.descripcion.ilike(pattern))
            )

        if disponible is not None:
            query = query.where(Producto.disponible == disponible)

        query = query.offset(offset).limit(limit)
        return list(self.session.exec(query).all())

    def get_destacados(self, limite: int = 6) -> List[Producto]:
        query = (
            select(Producto)
            .where(Producto.deleted_at.is_(None))
            .where(Producto.disponible == True)
            .limit(limite)
        )
        return list(self.session.exec(query).all())

    def get_by_id(self, id: int) -> Optional[Producto]:
        producto = self.session.get(Producto, id)
        if producto and producto.deleted_at is not None:
            return None
        return producto

    def create(self, nombre: str, descripcion: Optional[str], precio_base: float,
               imagenes_url: Optional[str], stock_cantidad: int, disponible: bool) -> Producto:
        producto = Producto(
            nombre=nombre, descripcion=descripcion, precio_base=precio_base,
            imagenes_url=imagenes_url, stock_cantidad=stock_cantidad, disponible=disponible,
        )
        self.session.add(producto)
        self.session.flush()
        return producto

    def add_categoria(self, producto_id: int, categoria_id: int, es_principal: bool = False) -> ProductoCategoria:
        link = ProductoCategoria(
            producto_id=producto_id, categoria_id=categoria_id, es_principal=es_principal
        )
        self.session.add(link)
        self.session.flush()
        return link

    def add_ingrediente(self, producto_id: int, ingrediente_id: int, es_removible: bool = False, es_alergeno: bool = False) -> ProductoIngrediente:
        link = ProductoIngrediente(
            producto_id=producto_id, ingrediente_id=ingrediente_id, es_removible=es_removible, es_alergeno=es_alergeno
        )
        self.session.add(link)
        self.session.flush()
        return link

    def update(self, id: int, data: "ProductoUpdate") -> Optional[Producto]:
        producto = self.get_by_id(id)
        if not producto:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(producto, key, value)
        self.session.flush()
        return producto

    def soft_delete(self, id: int) -> Optional[Producto]:
        producto = self.get_by_id(id)
        if not producto:
            return None

        # Limpiar relaciones para no bloquear eliminación de categorías/ingredientes
        for pc in producto.categorias:
            self.session.delete(pc)
        for pi in producto.ingredientes:
            self.session.delete(pi)

        producto.deleted_at = datetime.now()
        self.session.flush()
        return producto
