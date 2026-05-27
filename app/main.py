import os
import logging
from typing import Optional, List, Annotated
from fastapi import FastAPI, Query, Path, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# ⚡ Cargar variables de entorno ANTES de cualquier otro import de la app
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app.database import create_db_and_tables
from app.seed import run_seed
from app.categorias.router import router as categorias_router
from app.ingredientes.router import router as ingredientes_router
from app.productos.router import router as productos_router
from app.usuarios.router import router as usuarios_router
from app.pedidos.router import router as pedidos_router
from app.auth.router import router as auth_router
from app.direcciones.router import router as direcciones_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Burger House API",
    description="API para gestión de restaurant de hamburguesas",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({"field": field, "message": err.get("msg", "Error de validación")})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Error de validación", "errors": errors},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )


app.include_router(auth_router)
app.include_router(categorias_router)
app.include_router(ingredientes_router)
app.include_router(productos_router)
app.include_router(usuarios_router)
app.include_router(pedidos_router)
app.include_router(direcciones_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    run_seed()


@app.get("/")
def root():
    return {"message": "Burger House API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}