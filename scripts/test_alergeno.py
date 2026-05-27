"""Test es_alergeno creation via repository."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from sqlmodel import Session, text
from app.database import engine
from app.models import SQLModel, ProductoIngrediente

# Ensure column exists
SQLModel.metadata.create_all(engine)

with Session(engine) as s:
    r = s.execute(
        text("SELECT column_name FROM information_schema.columns WHERE table_name = :t AND column_name = :c"),
        {"t": "producto_ingredientes", "c": "es_alergeno"},
    ).first()
    if r:
        print("OK: es_alergeno column exists")
    else:
        print("Adding es_alergeno column...")
        s.execute(text("ALTER TABLE producto_ingredientes ADD COLUMN es_alergeno BOOLEAN NOT NULL DEFAULT FALSE"))
        s.commit()
        print("OK: column added")

# Test repository
from app.productos.repository import ProductoRepository
from app.core import UnitOfWork

with UnitOfWork() as uow:
    repo = ProductoRepository(uow.session)
    link = repo.add_ingrediente(1, 1, es_removible=True, es_alergeno=True)
    print(f"OK: link id={link.id} es_removible={link.es_removible} es_alergeno={link.es_alergeno}")
    uow.rollback()

print("OK: es_alergeno works correctly")
