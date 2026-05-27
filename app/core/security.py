"""
Módulo de seguridad para Burger House.

Provee funciones de hash y verificación de contraseñas usando bcrypt
con cost factor 12, y utilidades JWT para autenticación.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt

# ──────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────

COST_FACTOR = 12
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "burger-house-secret-key-cambiame-en-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2 horas para desarrollo


# ──────────────────────────────────────────────
# Password Hashing (bcrypt)
# ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt con el cost factor configurado.
    """
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=COST_FACTOR))
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica una contraseña contra su hash de bcrypt.
    """
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ──────────────────────────────────────────────
# JWT Tokens
# ──────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT access token.

    Args:
        data: Datos a incluir en el payload (debe contener 'sub' con el user_id).
        expires_delta: Tiempo de expiración opcional (default: 30 min).

    Returns:
        String con el token JWT codificado.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica y verifica un JWT token.

    Args:
        token: Token JWT a decodificar.

    Returns:
        Payload decodificado si es válido, None si expiró o es inválido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
