"""
Migracion de SQLite a PostgreSQL.

Uso: python scripts/migrate_to_postgres.py
Requiere DATABASE_URL en .env apuntando a PostgreSQL.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from sqlmodel import Session, create_engine, text
from app.models import SQLModel
from app.database import engine as pg_engine
from app.seed import run_seed

# Orden correcto de insercion por dependencias de FK
TABLE_ORDER = [
    "roles",
    "estados_pedido",
    "formas_pago",
    "categorias",
    "ingredientes",
    "usuarios",
    "productos",
    "producto_categorias",
    "producto_ingredientes",
    "pedidos",
    "historial_estados",
    "pedido_detalles",
]

# Columnas booleanas SQLite (0/1) -> PostgreSQL (true/false)
BOOLEAN_COLS = {
    "categorias": ["es_activa"],
    "producto_categorias": ["es_principal"],
    "producto_ingredientes": ["es_removible"],
    "productos": ["disponible"],
    "ingredientes": ["disponible"],
}


def fix_row(table_name: str, columns: list, row: tuple) -> dict:
    data = dict(zip(columns, row))
    for col in BOOLEAN_COLS.get(table_name, []):
        if col in data and data[col] is not None:
            data[col] = bool(data[col])
    return data


def migrate_data():
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "burgerhouse.db")

    if not os.path.exists(sqlite_path):
        print("[SKIP] No se encontro burgerhouse.db. Se creara base limpia en PostgreSQL.")
        SQLModel.metadata.create_all(pg_engine)
        return

    sqlite_engine = create_engine(
        f"sqlite:///{sqlite_path}",
        connect_args={"check_same_thread": False},
    )

    with sqlite_engine.connect() as sqlite_conn:
        # Obtener datos de SQLite como dicts
        all_data = {}
        for table in TABLE_ORDER:
            result = sqlite_conn.execute(text(f"SELECT * FROM {table}"))
            rows = result.fetchall()
            columns = list(result.keys())
            all_data[table] = [fix_row(table, columns, row) for row in rows]
            print(f"  [SQLite] {table}: {len(rows)} registros")

    # Recrear tablas en PostgreSQL
    print("\nRecreando tablas en PostgreSQL...")
    SQLModel.metadata.drop_all(pg_engine)
    SQLModel.metadata.create_all(pg_engine)

    # Insertar en orden
    with Session(pg_engine) as pg_session:
        for table in TABLE_ORDER:
            rows = all_data.get(table, [])
            if not rows:
                print(f"  {table}: 0 registros")
                continue

            col_names = ", ".join(rows[0].keys())
            placeholders = ", ".join([f":{c}" for c in rows[0].keys()])

            for row in rows:
                pg_session.execute(
                    text(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"),
                    row,
                )
            pg_session.commit()
            print(f"  {table}: {len(rows)} registros migrados")

    print("\n Migracion completada exitosamente.")


if __name__ == "__main__":
    print("Migrando SQLite -> PostgreSQL...")
    print(f"URL: {os.getenv('DATABASE_URL', 'no configurada')}")
    migrate_data()
    print("\nEjecutando seed...")
    try:
        run_seed()
        print(" Seed OK (datos existentes no duplicados).")
    except Exception as e:
        print(f" Seed: {e}")
    print("\n Listo!")
