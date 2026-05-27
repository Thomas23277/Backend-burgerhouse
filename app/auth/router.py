"""Router de autenticación."""
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from app.models import Usuario
from app.auth.schemas import LoginRequest, RegisterRequest, MeResponse, LoginResponse
from app.auth import service
from app.core.dependencies import get_current_user

router = APIRouter(tags=["auth"])

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 7200  # 2 horas en segundos


@router.post(
    "/auth/register",
    response_model=MeResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: RegisterRequest):
    """Registra un nuevo usuario con rol CLIENT automático."""
    return service.register(data)


@router.post("/auth/login", response_model=LoginResponse)
def login(data: LoginRequest):
    """Inicia sesión y setea cookie httpOnly con JWT."""
    response_data, token = service.login(data)

    resp = JSONResponse(content=response_data.model_dump(mode="json"))
    resp.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=False,  # False en desarrollo, True en prod con HTTPS
    )
    return resp


@router.get("/auth/me", response_model=MeResponse)
def me(usuario: Usuario = Depends(get_current_user)):
    """Retorna los datos del usuario autenticado."""
    return service.get_me(usuario)


@router.post("/auth/logout")
def logout():
    """Elimina la cookie de acceso."""
    resp = JSONResponse(content={"message": "Sesión cerrada correctamente"})
    resp.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        samesite="lax",
    )
    return resp
