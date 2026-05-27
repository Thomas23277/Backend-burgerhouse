"""Service de autenticación."""
from fastapi import HTTPException, status
from app.usuarios.repository import UsuarioRepository
from app.usuarios.schemas import UsuarioCreate
from app.auth.schemas import LoginRequest, RegisterRequest, MeResponse, LoginResponse
from app.core import UnitOfWork
from app.core.security import hash_password, verify_password, create_access_token


def register(data: RegisterRequest) -> MeResponse:
    """Registra un nuevo usuario con rol CLIENT automático."""
    with UnitOfWork() as uow:
        repo = UsuarioRepository(uow.session)

        existing = repo.get_by_username(data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya existe",
            )

        hashed = hash_password(data.password)
        usuario = repo.create(
            username=data.username,
            email=data.email,
            nombre=data.nombre,
            rol="cliente",
            hashed_password=hashed,
        )
        return MeResponse(
            id=usuario.id,
            username=usuario.username,
            email=usuario.email,
            nombre=usuario.nombre,
            rol=usuario.rol,
            created_at=usuario.created_at,
        )


def login(data: LoginRequest) -> tuple[LoginResponse, str]:
    """
    Autentica un usuario por email y password.

    Returns:
        Tupla de (LoginResponse, token_string).
    """
    with UnitOfWork() as uow:
        repo = UsuarioRepository(uow.session)
        # Buscar por email
        usuarios = repo.get_all()
        usuario = next((u for u in usuarios if u.email == data.email), None)

        if not usuario or not verify_password(data.password, usuario.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
            )

        token = create_access_token({"sub": str(usuario.id)})
        response_data = LoginResponse(
            message="Inicio de sesión exitoso",
            usuario=MeResponse(
                id=usuario.id,
                username=usuario.username,
                email=usuario.email,
                nombre=usuario.nombre,
                rol=usuario.rol,
                created_at=usuario.created_at,
            ),
        )
        return response_data, token


def get_me(usuario) -> MeResponse:
    """Retorna la información del usuario autenticado."""
    return MeResponse(
        id=usuario.id,
        username=usuario.username,
        email=usuario.email,
        nombre=usuario.nombre,
        rol=usuario.rol,
        created_at=usuario.created_at,
    )
