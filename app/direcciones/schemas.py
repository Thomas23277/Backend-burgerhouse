from typing import Optional
from pydantic import BaseModel, Field


class DireccionBase(BaseModel):
    alias: str = Field(min_length=1, max_length=50)
    direccion: str = Field(min_length=1, max_length=255)
    ciudad: str = Field(min_length=1, max_length=100)
    codigo_postal: str = Field(min_length=1, max_length=20)


class DireccionCreate(DireccionBase):
    es_principal: bool = False


class DireccionUpdate(BaseModel):
    alias: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_principal: Optional[bool] = None


class DireccionResponse(DireccionBase):
    id: int
    usuario_id: int
    es_principal: bool

    class Config:
        from_attributes = True
