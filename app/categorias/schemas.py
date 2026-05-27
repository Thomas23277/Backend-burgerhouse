from typing import Optional, List
from pydantic import BaseModel, Field


class CategoriaBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None
    es_activa: bool = True


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None
    es_activa: Optional[bool] = None


class CategoriaResponse(CategoriaBase):
    id: int
    subcategorias: List["CategoriaResponse"] = []

    class Config:
        from_attributes = True


CategoriaResponse.model_rebuild()
