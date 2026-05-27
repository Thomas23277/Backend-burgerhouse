"""Schemas para autenticación."""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LoginRequest(BaseModel):
    email: str = Field(max_length=200)
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(max_length=200)
    password: str = Field(min_length=6)
    nombre: str


class MeResponse(BaseModel):
    id: int
    username: str
    email: str
    nombre: str
    rol: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    message: str
    usuario: MeResponse
