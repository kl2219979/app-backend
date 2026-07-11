"""
app/main.py — Arranque de FastAPI
---------------------------------

QUÉ ES
    El archivo que Uvicorn carga: `uvicorn app.main:app`.
    Construye la aplicación HTTP (rutas, CORS, docs).

POR QUÉ EXISTE
    Necesitas un único punto de entrada claro para el servidor.
    Aquí se "arma" la API; la lógica de negocio vive en otras carpetas.

QUÉ NO HACE
    No crea tablas ni corre Alembic.
    Eso ya ocurrió en entrypoint.sh / migrate.sh antes de servir tráfico.

PARTES
    - lifespan: código al encender/apagar (ahora vacío a propósito)
    - CORS: permite que el frontend en Vite llame a esta API
    - api_router: monta todas las rutas bajo /api/v1
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Se ejecuta al arrancar y al apagar la app. Hoy no necesita setup extra."""
    yield


def create_app() -> FastAPI:
    """Arma la instancia FastAPI con middleware y routers."""
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
        # En producción ocultamos Swagger para no exponer la API pública.
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Sin CORS, el navegador bloquearía llamadas desde http://localhost:5173.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
