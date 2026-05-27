"""Reset sequences after manual inserts."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
from sqlmodel import Session, text
from app.database import engine

tables = [
    'pedidos', 'pedido_detalles', 'historial_estados', 'usuarios',
    'categorias', 'productos', 'ingredientes', 'direcciones',
    'producto_categorias', 'producto_ingredientes',
]
queries = [
    f"SELECT setval('{t}_id_seq', COALESCE((SELECT MAX(id) FROM {t}), 0))"
    for t in tables
]
with Session(engine) as s:
    for q in queries:
        r = s.execute(text(q)).scalar()
        print(f"{q.split('(')[0].strip()} -> {r}")
    s.commit()
    for tbl in tables:
        r = s.execute(text(f"SELECT currval('{tbl}_id_seq')")).scalar()
        print(f"  {tbl}_id_seq = {r}")
