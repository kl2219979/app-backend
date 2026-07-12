"""
app/api/v1/endpoints/auth.py — Registro y login
===============================================

QUÉ ES
------
Endpoints públicos de autenticación:
  POST /auth/register → crea usuario (guarda hash, no la clave en claro)
  POST /auth/login    → verifica clave y devuelve JWT
  GET  /auth/me       → perfil del usuario del token (ruta protegida)

PRINCIPIO
---------
El endpoint orquesta HTTP; el hashing/JWT está en app.core.security;
la sesión de BD viene de Depends(get_db).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import Token, UserPublic, UserRegister

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
)
def register(body: UserRegister, db: Session = Depends(get_db)) -> User:
    """
    Crea un usuario nuevo.

    - Comprueba que correo/usuario no existan.
    - Hashea la contraseña con bcrypt antes de guardar.
    - Nunca persiste `contrasena` en texto plano.
    """
    existing = db.scalar(
        select(User).where(
            or_(User.correo == body.correo, User.usuario == body.usuario)
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese correo o nombre de usuario",
        )

    user = User(
        nombres=body.nombres,
        apellidos=body.apellidos,
        fecha_nacimiento=body.fecha_nacimiento,
        genero=body.genero,
        correo=body.correo,
        usuario=body.usuario,
        contrasena_hash=hash_password(body.contrasena),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login (OAuth2 password) → JWT",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """
    Autentica con usuario/correo + contraseña (formulario x-www-form-urlencoded).

    Campos del form (estándar OAuth2):
      - username: puede ser `usuario` O `correo`
      - password: contraseña en texto plano (solo viaja en esta request)

    Respuesta: { "access_token": "...", "token_type": "bearer" }
    Swagger usa este endpoint en el botón Authorize.
    """
    user = db.scalar(
        select(User).where(
            or_(
                User.usuario == form_data.username,
                User.correo == form_data.username,
            )
        )
    )
    if user is None or not verify_password(form_data.password, user.contrasena_hash):
        # Mensaje genérico: no revelar si falló el usuario o la clave.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user.id)
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Usuario autenticado",
)
def me(current_user: User = Depends(get_current_user)) -> User:
    """Ejemplo de ruta protegida: requiere header Authorization: Bearer <token>."""
    return current_user
