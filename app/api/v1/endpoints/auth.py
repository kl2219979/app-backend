"""
app/api/v1/endpoints/auth.py — Registro, login, refresh, logout, me
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LogoutRequest, RefreshRequest, Token, UserPublic, UserRegister
from app.services.auth import AuthService

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
)
def register(body: UserRegister, db: Session = Depends(get_db)) -> User:
    return AuthService.register(db, body)


@router.post(
    "/login",
    response_model=Token,
    summary="Login (OAuth2 password) → access + refresh",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    return AuthService.login(db, form_data.username, form_data.password)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Renovar access token con refresh token",
)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> Token:
    return AuthService.refresh(db, body.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revocar refresh token (o todos los del usuario)",
)
def logout(
    body: LogoutRequest = LogoutRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    if body.refresh_token:
        AuthService.logout(db, body.refresh_token)
    else:
        AuthService.logout(db, user=current_user)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Usuario autenticado",
)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
