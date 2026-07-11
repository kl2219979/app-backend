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

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
