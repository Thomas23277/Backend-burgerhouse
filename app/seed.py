"""
Seed data completo para Burger House.

Se ejecuta automáticamente al iniciar la aplicación y es IDEMPOTENTE:
verifica existencia antes de insertar para no duplicar registros.

Incluye:
  - Roles: ADMIN, STOCK, PEDIDOS, CLIENT
  - Estados de Pedido: PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO
  - Formas de Pago: Efectivo, Tarjeta
  - Usuario administrador por defecto: admin@burger.com
  - Categorías, Ingredientes y Productos con imágenes reales
"""

from typing import Optional
from sqlmodel import Session, select
from app.database import engine
from app.models import (
    Usuario, Rol, EstadoPedido, FormaPago,
    Categoria, Ingrediente, Producto,
    ProductoCategoria, ProductoIngrediente,
)
from app.usuarios.repository import UsuarioRepository
from app.core.security import hash_password

# ──────────────────────────────────────────────
# Datos a seedear — Catálogos base
# ──────────────────────────────────────────────

ROLES = [
    {"codigo": "ADMIN", "nombre": "Administrador", "descripcion": "Acceso completo al sistema"},
    {"codigo": "STOCK", "nombre": "Gestor de Stock", "descripcion": "Lectura de productos y actualización de stock"},
    {"codigo": "PEDIDOS", "nombre": "Gestor de Pedidos", "descripcion": "Visualización y avance de estados de pedidos"},
    {"codigo": "CLIENT", "nombre": "Cliente", "descripcion": "Catálogo, carrito y pedidos propios"},
]

ESTADOS_PEDIDO = [
    {"codigo": "PENDIENTE", "nombre": "Pendiente", "descripcion": "Pedido creado, esperando confirmación"},
    {"codigo": "CONFIRMADO", "nombre": "Confirmado", "descripcion": "Pedido confirmado, en espera de preparación"},
    {"codigo": "EN_PREP", "nombre": "En Preparación", "descripcion": "Pedido siendo preparado en cocina"},
    {"codigo": "EN_CAMINO", "nombre": "En Camino", "descripcion": "Pedido en camino al cliente"},
    {"codigo": "ENTREGADO", "nombre": "Entregado", "descripcion": "Pedido entregado al cliente"},
    {"codigo": "CANCELADO", "nombre": "Cancelado", "descripcion": "Pedido cancelado"},
]

FORMAS_PAGO = [
    {"codigo": "EFECTIVO", "nombre": "Efectivo", "descripcion": "Pago en efectivo al recibir"},
    {"codigo": "TARJETA", "nombre": "Tarjeta", "descripcion": "Pago con tarjeta de crédito/débito"},
]

ADMIN_DEFAULT = {
    "username": "admin",
    "email": "admin@burger.com",
    "password": "Admin123!",
    "nombre": "Administrador del Sistema",
    "rol": "admin",
}

# ──────────────────────────────────────────────
# Categorías
# ──────────────────────────────────────────────

CATEGORIAS = [
    {
        "nombre": "Hamburguesas",
        "descripcion": "Nuestras hamburguesas artesanales, hechas con carne 100% de res",
        "imagen_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
    },
    {
        "nombre": "Papas y Acompañamientos",
        "descripcion": "Las mejores papas fritas y acompañamientos para tu burger",
        "imagen_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400",
    },
    {
        "nombre": "Bebidas",
        "descripcion": "Refrescos, aguas y bebidas para acompañar tu pedido",
        "imagen_url": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400",
    },
    {
        "nombre": "Postres",
        "descripcion": "El mejor cierre dulce para tu experiencia Burger House",
        "imagen_url": "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400",
    },
]

# ──────────────────────────────────────────────
# Ingredientes
# ──────────────────────────────────────────────

INGREDIENTES = [
    {"nombre": "Pan de hamburguesa", "descripcion": "Pan artesanal brioche", "precio_adicional": 0, "imagen_url": "https://images.unsplash.com/photo-1509365465985-25d11c17e812?w=200"},
    {"nombre": "Carne de res 200g", "descripcion": "Carne angus 100% de res", "precio_adicional": 0, "imagen_url": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=200"},
    {"nombre": "Queso cheddar", "descripcion": "Queso cheddar derretido", "precio_adicional": 500, "imagen_url": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=200"},
    {"nombre": "Queso suizo", "descripcion": "Queso suizo fundido", "precio_adicional": 600, "imagen_url": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=200"},
    {"nombre": "Lechuga fresca", "descripcion": "Lechuga criolla fresca", "precio_adicional": 0, "imagen_url": "https://images.unsplash.com/photo-1556801712-76c8eb07bbc9?w=200"},
    {"nombre": "Tomate", "descripcion": "Tomate fresco en rodajas", "precio_adicional": 0, "imagen_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=200"},
    {"nombre": "Cebolla morada", "descripcion": "Cebolla morada en aros", "precio_adicional": 0, "imagen_url": "https://images.unsplash.com/photo-1508747703724-2c2e79e52e34?w=200"},
    {"nombre": "Pepinillos", "descripcion": "Pepinillos en rodajas", "precio_adicional": 300, "imagen_url": "https://images.unsplash.com/photo-1607532941433-3046591e1a5e?w=200"},
    {"nombre": "Bacon crocante", "descripcion": "Tiras de bacon ahumado", "precio_adicional": 1000, "imagen_url": "https://images.unsplash.com/photo-1559742811-822f4580b12e?w=200"},
    {"nombre": "Salsa BBQ", "descripcion": "Salsa barbacoa ahumada", "precio_adicional": 0, "imagen_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=200"},
    {"nombre": "Salsa especial", "descripcion": "Salsa secreta de la casa", "precio_adicional": 0, "imagen_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=200"},
    {"nombre": "Huevo", "descripcion": "Huevo frito", "precio_adicional": 500, "imagen_url": "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?w=200"},
    {"nombre": "Jalapeño", "descripcion": "Jalapeños frescos en rodajas", "precio_adicional": 400, "imagen_url": "https://images.unsplash.com/photo-1582347613265-1e9b69b2c130?w=200"},
    {"nombre": "Salsa de queso", "descripcion": "Salsa de queso cheddar para acompañar", "precio_adicional": 800, "imagen_url": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=200"},
]

# ──────────────────────────────────────────────
# Productos con sus relaciones
# ──────────────────────────────────────────────
# Cada producto tiene: nombre, descripcion, precio, imagen_url,
# stock, categorias (lista de tuplas (nombre_categoria, es_principal)),
# ingredientes (lista de tuplas (nombre_ingrediente, es_removible, es_alergeno))

PRODUCTOS = [
    {
        "nombre": "Clásica Burger",
        "descripcion": "La clásica burger con carne angus, lechuga, tomate, cebolla morada y salsa especial",
        "precio_base": 5500,
        "imagenes_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600",
        "stock_cantidad": 50,
        "disponible": True,
        "categorias": [("Hamburguesas", True)],
        "ingredientes": [
            ("Pan de hamburguesa", False, False),
            ("Carne de res 200g", False, False),
            ("Queso cheddar", False, True),
            ("Lechuga fresca", True, False),
            ("Tomate", True, False),
            ("Cebolla morada", True, False),
            ("Salsa especial", False, False),
        ],
    },
    {
        "nombre": "BBQ Bacon Burger",
        "descripcion": "Burger con bacon crocante, queso cheddar, cebolla morada y salsa BBQ ahumada",
        "precio_base": 7500,
        "imagenes_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=600",
        "stock_cantidad": 40,
        "disponible": True,
        "categorias": [("Hamburguesas", True)],
        "ingredientes": [
            ("Pan de hamburguesa", False, False),
            ("Carne de res 200g", False, False),
            ("Bacon crocante", True, False),
            ("Queso cheddar", False, True),
            ("Cebolla morada", True, False),
            ("Salsa BBQ", False, False),
        ],
    },
    {
        "nombre": "Suiza Burger",
        "descripcion": "Burger con queso suizo fundido, lechuga, tomate y salsa especial",
        "precio_base": 6500,
        "imagenes_url": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=600",
        "stock_cantidad": 35,
        "disponible": True,
        "categorias": [("Hamburguesas", True)],
        "ingredientes": [
            ("Pan de hamburguesa", False, False),
            ("Carne de res 200g", False, False),
            ("Queso suizo", False, True),
            ("Lechuga fresca", True, False),
            ("Tomate", True, False),
            ("Salsa especial", False, False),
        ],
    },
    {
        "nombre": "Picante Burger",
        "descripcion": "Para los valientes: burger con jalapeños, queso cheddar y salsa especial",
        "precio_base": 7000,
        "imagenes_url": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=600",
        "stock_cantidad": 30,
        "disponible": True,
        "categorias": [("Hamburguesas", True)],
        "ingredientes": [
            ("Pan de hamburguesa", False, False),
            ("Carne de res 200g", False, False),
            ("Jalapeño", True, False),
            ("Queso cheddar", False, True),
            ("Cebolla morada", True, False),
            ("Salsa especial", False, False),
        ],
    },
    {
        "nombre": "Completa Burger",
        "descripcion": "La burger más completa: bacon, huevo, queso cheddar, lechuga, tomate, pepinillos y salsa especial",
        "precio_base": 9000,
        "imagenes_url": "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=600",
        "stock_cantidad": 25,
        "disponible": True,
        "categorias": [("Hamburguesas", True)],
        "ingredientes": [
            ("Pan de hamburguesa", False, False),
            ("Carne de res 200g", False, False),
            ("Bacon crocante", True, False),
            ("Huevo", True, False),
            ("Queso cheddar", False, True),
            ("Lechuga fresca", True, False),
            ("Tomate", True, False),
            ("Pepinillos", True, False),
            ("Salsa especial", False, False),
        ],
    },
    {
        "nombre": "Papas Fritas",
        "descripcion": "Papas fritas crocantes con sal marina",
        "precio_base": 2500,
        "imagenes_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=600",
        "stock_cantidad": 100,
        "disponible": True,
        "categorias": [("Papas y Acompañamientos", True)],
        "ingredientes": [],
    },
    {
        "nombre": "Aros de Cebolla",
        "descripcion": "Aros de cebolla empanizados y fritos, servidos con salsa de queso",
        "precio_base": 3000,
        "imagenes_url": "https://images.unsplash.com/photo-1639024471283-03518883512d?w=600",
        "stock_cantidad": 60,
        "disponible": True,
        "categorias": [("Papas y Acompañamientos", True)],
        "ingredientes": [
            ("Cebolla morada", False, False),
            ("Salsa de queso", False, True),
        ],
    },
    {
        "nombre": "Papas con Queso y Bacon",
        "descripcion": "Papas fritas cubiertas con salsa de queso cheddar y bacon crocante",
        "precio_base": 4500,
        "imagenes_url": "https://images.unsplash.com/photo-1606755456209-6b7a2b280f2b?w=600",
        "stock_cantidad": 45,
        "disponible": True,
        "categorias": [("Papas y Acompañamientos", True)],
        "ingredientes": [
            ("Bacon crocante", True, False),
            ("Salsa de queso", False, True),
        ],
    },
    {
        "nombre": "Coca Cola 500ml",
        "descripcion": "Coca Cola clásica en envase de 500ml",
        "precio_base": 1500,
        "imagenes_url": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=600",
        "stock_cantidad": 200,
        "disponible": True,
        "categorias": [("Bebidas", True)],
        "ingredientes": [],
    },
    {
        "nombre": "Sprite 500ml",
        "descripcion": "Sprite bien fría en envase de 500ml",
        "precio_base": 1500,
        "imagenes_url": "https://images.unsplash.com/photo-1624517452488-0482c908d0c4?w=600",
        "stock_cantidad": 200,
        "disponible": True,
        "categorias": [("Bebidas", True)],
        "ingredientes": [],
    },
    {
        "nombre": "Agua Mineral 500ml",
        "descripcion": "Agua mineral sin gas en envase de 500ml",
        "precio_base": 1000,
        "imagenes_url": "https://images.unsplash.com/photo-1560023907-5f3399ea0ddf?w=600",
        "stock_cantidad": 200,
        "disponible": True,
        "categorias": [("Bebidas", True)],
        "ingredientes": [],
    },
    {
        "nombre": "Limonada",
        "descripcion": "Limonada natural fresca con hielo",
        "precio_base": 2000,
        "imagenes_url": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=600",
        "stock_cantidad": 80,
        "disponible": True,
        "categorias": [("Bebidas", True)],
        "ingredientes": [],
    },
    {
        "nombre": "Helado de Vainilla",
        "descripcion": "Helado cremoso de vainilla con toppings a elección",
        "precio_base": 2500,
        "imagenes_url": "https://images.unsplash.com/photo-1505394033641-40f6ad2718bd?w=600",
        "stock_cantidad": 50,
        "disponible": True,
        "categorias": [("Postres", True)],
        "ingredientes": [],
    },
    {
        "nombre": "Brownie con Helado",
        "descripcion": "Brownie de chocolate caliente servido con helado de vainilla",
        "precio_base": 3500,
        "imagenes_url": "https://images.unsplash.com/photo-1564355808539-22e50a3f3a0c?w=600",
        "stock_cantidad": 30,
        "disponible": True,
        "categorias": [("Postres", True)],
        "ingredientes": [],
    },
]

# ──────────────────────────────────────────────
# Helpers de idempotencia
# ──────────────────────────────────────────────

def _seed_catalogo(session: Session, model, items: list, unique_field: str):
    """
    Inserta registros de un catálogo si no existen.
    `unique_field` es el atributo usado para verificar existencia (ej: "codigo").
    """
    for item in items:
        existing = session.exec(
            select(model).where(getattr(model, unique_field) == item[unique_field])
        ).first()
        if existing is None:
            session.add(model(**item))


def _seed_admin(session: Session):
    """Crea el usuario administrador por defecto si no existe."""
    repo = UsuarioRepository(session)
    existing = repo.get_by_username(ADMIN_DEFAULT["username"])
    if existing is None:
        hashed = hash_password(ADMIN_DEFAULT['password'])
        repo.create(
            username=ADMIN_DEFAULT["username"],
            email=ADMIN_DEFAULT["email"],
            nombre=ADMIN_DEFAULT["nombre"],
            rol=ADMIN_DEFAULT["rol"],
            hashed_password=hashed,
        )


def _seed_categorias(session: Session):
    """Crea las categorías si no existen."""
    for cat in CATEGORIAS:
        existing = session.exec(
            select(Categoria).where(Categoria.nombre == cat["nombre"])
        ).first()
        if existing is None:
            session.add(Categoria(**cat))


def _seed_ingredientes(session: Session):
    """Crea los ingredientes si no existen."""
    for ing in INGREDIENTES:
        existing = session.exec(
            select(Ingrediente).where(Ingrediente.nombre == ing["nombre"])
        ).first()
        if existing is None:
            session.add(Ingrediente(**ing))


def _get_nombre_map(session: Session, model):
    """Devuelve un dict {nombre: objeto} para búsquedas rápidas."""
    resultados = session.exec(select(model)).all()
    return {r.nombre: r for r in resultados}


def _seed_productos(session: Session):
    """Crea los productos con sus relaciones a categorías e ingredientes."""
    categorias_map = _get_nombre_map(session, Categoria)
    ingredientes_map = _get_nombre_map(session, Ingrediente)

    for prod_data in PRODUCTOS:
        # Verificar si el producto ya existe
        existing = session.exec(
            select(Producto).where(Producto.nombre == prod_data["nombre"])
        ).first()
        if existing is not None:
            continue

        # Crear producto base
        categorias_list = prod_data.pop("categorias")
        ingredientes_list = prod_data.pop("ingredientes")
        producto = Producto(**prod_data)
        session.add(producto)
        session.flush()

        # Asociar categorías
        for cat_nombre, es_principal in categorias_list:
            cat = categorias_map.get(cat_nombre)
            if cat:
                session.add(ProductoCategoria(
                    producto_id=producto.id,
                    categoria_id=cat.id,
                    es_principal=es_principal,
                ))

        # Asociar ingredientes
        for ing_nombre, es_removible, es_alergeno in ingredientes_list:
            ing = ingredientes_map.get(ing_nombre)
            if ing:
                session.add(ProductoIngrediente(
                    producto_id=producto.id,
                    ingrediente_id=ing.id,
                    es_removible=es_removible,
                    es_alergeno=es_alergeno,
                ))


# ──────────────────────────────────────────────
# Función principal
# ──────────────────────────────────────────────

def run_seed():
    """Ejecuta el seed de datos obligatorio. Idempotente."""
    with Session(engine) as session:
        _seed_catalogo(session, Rol, ROLES, "codigo")
        _seed_catalogo(session, EstadoPedido, ESTADOS_PEDIDO, "codigo")
        _seed_catalogo(session, FormaPago, FORMAS_PAGO, "codigo")
        _seed_admin(session)
        _seed_categorias(session)
        _seed_ingredientes(session)
        session.flush()
        _seed_productos(session)
        session.commit()
