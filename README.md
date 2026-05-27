# 🖥️ Burger House — Backend API

API RESTful para el sistema de gestión de restaurante **Burger House**, desarrollada con **FastAPI + SQLModel + PostgreSQL**.

## 🎥 Video de Presentación

**Link del video:** _[PENDIENTE — agregar link de YouTube cuando esté subido]_

---

## 🛠️ Tecnologías

- **FastAPI** — Framework web moderno de Python
- **SQLModel** — ORM con validación Pydantic
- **PostgreSQL** — Base de datos principal
- **JWT + bcrypt** — Autenticación con cookies httpOnly
- **Unit of Work + Repository** — Patrones de persistencia
- **Máquina de Estados** — State machine para pedidos con Audit Trail
- **Snapshot Pattern** — Precios inmutables en DetallePedido

## 🚀 Ejecución

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Disponible en: http://127.0.0.1:8000
Documentación Swagger: http://127.0.0.1:8000/docs

## 📁 Estructura

```
backend/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── models.py            # Modelos SQLModel (tablas)
│   ├── database.py          # Conexión PostgreSQL
│   ├── seed.py              # Seed obligatorio idempotente
│   ├── auth/                # Autenticación (router, schemas, service)
│   ├── categorias/          # CRUD categorías
│   ├── ingredientes/        # CRUD ingredientes
│   ├── productos/           # CRUD productos
│   ├── pedidos/             # Pedidos + máquina de estados
│   ├── usuarios/            # CRUD usuarios
│   ├── direcciones/         # Direcciones de entrega
│   └── core/                # Seguridad, dependencias, Unit of Work
├── requirements.txt
└── .env
```

## 👤 Credenciales de Prueba

| Usuario | Email | Contraseña | Rol |
|---------|-------|------------|-----|
| `admin` | `admin@burger.com` | `Admin123!` | ADMIN (acceso completo) |

> El seed se ejecuta automáticamente al iniciar la API. Es **idempotente** — no duplica datos.

## 🔐 Roles del Sistema

| Rol | Código | Capacidades |
|-----|--------|-------------|
| Administrador | ADMIN | CRUD completo |
| Gestor de Stock | STOCK | Leer productos, actualizar stock |
| Gestor de Pedidos | PEDIDOS | Ver y avanzar estados |
| Cliente | CLIENT | Catálogo, carrito, pedidos propios |
