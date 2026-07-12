"""
app/api/deps.py — Dependencias inyectables de FastAPI
=====================================================

QUÉ ES
------
Funciones que FastAPI inyecta en endpoints con Depends(...):
  - get_db           → sesión SQLAlchemy por request
  - get_current_user → usuario autenticado a partir del JWT

PRINCIPIO
---------
Cada request obtiene recursos frescos (sesión, usuario) y los libera al terminar.
No hay Session ni User “singleton” compartido entre requests.
"""

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_subject_from_token
from app.db.session import SessionLocal
from app.models.user import User

# tokenUrl: ruta donde el cliente obtiene el token (Swagger "Authorize" la usa).
# Debe coincidir con el endpoint real de login (prefijo /api/v1 incluido).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    """
    Abre una sesión de BD por request y la cierra al final (éxito o error).

    Uso:
        def endpoint(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependencia de rutas protegidas.

    Flujo
    -----
    1. OAuth2PasswordBearer lee el header: Authorization: Bearer <token>
    2. Decodificamos el JWT y leemos `sub` (user id).
    3. Cargamos el User desde Postgres.
    4. Si algo falla → 401 Unauthorized.

    Uso
    ---
        @router.get("/me")
        def me(current_user: User = Depends(get_current_user)):
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = int(get_subject_from_token(token))
    except (InvalidTokenError, ValueError):
        raise credentials_exception from None

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_exception

    return user
