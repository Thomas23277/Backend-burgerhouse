from typing import Optional
from pydantic import BaseModel, Field


class IngredienteBase(BaseModel):
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    precio_adicional: float = 0.0
    imagen_url: Optional[str] = None
    disponible: bool = True
    alergeno: bool = False


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_adicional: Optional[float] = None
    imagen_url: Optional[str] = None
    disponible: Optional[bool] = None
    alergeno: Optional[bool] = None


class IngredienteResponse(IngredienteBase):
    id: int

    class Config:
        from_attributes = True
