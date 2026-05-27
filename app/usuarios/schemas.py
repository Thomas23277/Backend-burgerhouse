from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UsuarioBase(BaseModel):
    username: str = Field(max_length=100)
    email: str = Field(max_length=200)
    nombre: str
    rol: str = "cliente"


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
