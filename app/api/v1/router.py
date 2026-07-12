"""
app/api/v1/router.py — Índice de rutas v1
"""

from fastapi import APIRouter

from app.api.v1.endpoints import account
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import category
from app.api.v1.endpoints import health
from app.api.v1.endpoints import sub_category
from app.api.v1.endpoints import transaction
from app.api.v1.endpoints import users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router)
api_router.include_router(account.router)
api_router.include_router(category.router)
api_router.include_router(sub_category.router)
api_router.include_router(transaction.router)
