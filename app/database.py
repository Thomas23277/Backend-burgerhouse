import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///burgerhouse.db",
)


def _create_sqlite_engine():
    from sqlalchemy.pool import StaticPool

    return create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_postgres_engine():
    return create_engine(DATABASE_URL)


if DATABASE_URL.startswith("postgresql"):
    engine = _create_postgres_engine()
else:
    engine = _create_sqlite_engine()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
