"""Script para probar login y direcciones."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app.database import engine
from app.core.security import verify_password, hash_password
from sqlmodel import Session, text

with Session(engine) as s:
    r = s.execute(text("SELECT id, email, hashed_password FROM usuarios WHERE id=1")).one()
    print(f"Email: {r[1]}")
    print(f"Hash: {r[2][:40]}...")
    print(f"Verify 'admin123': {verify_password('admin123', r[2])}")
    print(f"Verify 'Admin123!': {verify_password('Admin123!', r[2])}")

    # Probar crear direccion directamente en DB
    from app.models import DireccionEntrega
    from datetime import datetime
    d = DireccionEntrega(usuario_id=1, alias="Casa", direccion="Av. Siempre Viva 123",
                         ciudad="Cordoba", codigo_postal="5000", es_principal=True)
    s.add(d)
    s.commit()
    print(f"\nDireccion creada: id={d.id} alias={d.alias}")

    # Listar
    r2 = s.execute(text("SELECT id, alias, es_principal FROM direcciones WHERE deleted_at IS NULL")).all()
    for row in r2:
        print(f"  id={row[0]} alias={row[1]} principal={row[2]}")
