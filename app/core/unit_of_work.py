from sqlmodel import Session
from app.database import engine


class UnitOfWork:
    def __init__(self):
        self.session = None

    def __enter__(self):
        self.session = Session(engine, expire_on_commit=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
