from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CategoriaInput(BaseModel):
    categoria_id: int
    es_principal: bool = False


class IngredienteInput(BaseModel):
    ingrediente_id: int
    es_removible: bool = False
    es_alergeno: bool = False


class ProductoBase(BaseModel):
    nombre: str = Field(max_length=200)
    descripcion: Optional[str] = None
    precio_base: float
    imagenes_url: Optional[str] = None
    stock_cantidad: int = 0
    disponible: bool = True


class ProductoCreate(ProductoBase):
    categorias: List[CategoriaInput] = []
    ingredientes: List[IngredienteInput] = []


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagenes_url: Optional[str] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None


class CategoriaNested(BaseModel):
    id: int
    nombre: str
    imagen_url: Optional[str] = None
    es_principal: bool

    class Config:
        from_attributes = True


class IngredienteNested(BaseModel):
    id: int
    nombre: str
    precio_adicional: float
    imagen_url: Optional[str] = None
    alergeno: bool = False

    class Config:
        from_attributes = True


class ProductoResponse(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    categorias: List[CategoriaNested] = []
    ingredientes: List[IngredienteNested] = []

    class Config:
        from_attributes = True
