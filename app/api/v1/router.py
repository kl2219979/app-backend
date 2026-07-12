"""
app/api/v1/router.py
--------------------

QUÉ ES
    El "índice" de rutas de la versión 1 de la API.

POR QUÉ EXISTE
    Cada feature (health, users, ...) tiene su router.
    Aquí los juntas para montarlos todos bajo /api/v1 en main.py.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.api.v1.endpoints import category
from app.api.v1.endpoints import cuentas
from app.api.v1.endpoints import sub_category
from app.api.v1.endpoints import transacciones
from app.api.v1.endpoints import users


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(category.router, tags=["category"])
api_router.include_router(cuentas.router, tags=["cuentas"])
api_router.include_router(sub_category.router, tags=["sub_category"])
api_router.include_router(transacciones.router, tags=["transacciones"])
api_router.include_router(users.router, tags=["users"])
