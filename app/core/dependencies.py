"""
Dependencias de autenticación y autorización para FastAPI.

Provee:
- get_current_user: extrae usuario autenticado desde cookie JWT
- require_roles: verifica que el usuario tenga un rol permitido
"""

from typing import List, Callable
from fastapi import Request, HTTPException, status, Depends
from app.models import Usuario
from app.usuarios.repository import UsuarioRepository
from app.core import UnitOfWork
from app.core.security import decode_token

COOKIE_NAME = "access_token"


def get_current_user(request: Request) -> Usuario:
    """
    Extrae el usuario autenticado desde la cookie 'access_token'.

    Returns:
        Usuario autenticado.

    Raises:
        HTTPException 401: Si no hay token o es inválido.
        HTTPException 401: Si el usuario no existe o fue eliminado.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    with UnitOfWork() as uow:
        repo = UsuarioRepository(uow.session)
        usuario = repo.get_by_id(int(user_id))
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
            )
        return usuario


def require_roles(*allowed_roles: str) -> Callable:
    """
    Factory de dependencia que verifica que el usuario tenga uno de los roles permitidos.

    Uso:
        @router.get("/productos")
        def listar_productos(usuario: Usuario = Depends(require_roles("ADMIN", "STOCK"))):
            ...

    Args:
        allowed_roles: Roles permitidos para acceder al endpoint.

    Returns:
        Dependencia de FastAPI que retorna el usuario si tiene rol autorizado.
    """
    def role_checker(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol.upper() not in [r.upper() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles requeridos: {', '.join(allowed_roles)}",
            )
        return usuario
    return role_checker
