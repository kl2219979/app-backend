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
from app.api.v1.endpoints import account
from app.api.v1.endpoints import sub_category
from app.api.v1.endpoints import transaccion
from app.api.v1.endpoints import users


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(category.router, tags=["category"])
api_router.include_router(account.router, tags=["account"])
api_router.include_router(sub_category.router, tags=["sub_category"])
api_router.include_router(transaction.router, tags=["transaction"])
api_router.include_router(users.router, tags=["users"])
