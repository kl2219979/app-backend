"""
app/services/auth.py — Registro, login, refresh y logout
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import Token, UserRegister


class AuthService:
    @staticmethod
    def _issue_tokens(db: Session, user: User) -> Token:
        access = create_access_token(
            subject=user.id,
            extra_claims={"rol": user.rol},
        )
        raw_refresh = generate_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        RefreshTokenRepository.create(
            db,
            RefreshToken(
                user_id=user.id,
                token_hash=hash_refresh_token(raw_refresh),
                expires_at=expires_at,
            ),
        )
        db.commit()
        return Token(access_token=access, refresh_token=raw_refresh)

    @staticmethod
    def register(db: Session, body: UserRegister) -> User:
        if UserRepository.exists_correo_or_usuario(
            db, correo=body.correo, usuario=body.usuario
        ):
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
            rol="user",
        )
        UserRepository.create(db, user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, username: str, password: str) -> Token:
        user = UserRepository.get_by_correo_or_usuario(db, username)
        if user is None or not verify_password(password, user.contrasena_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta desactivada. Contacta soporte para reactivarla.",
            )
        return AuthService._issue_tokens(db, user)

    @staticmethod
    def refresh(db: Session, raw_refresh: str) -> Token:
        stored = RefreshTokenRepository.get_active_by_hash(
            db, hash_refresh_token(raw_refresh)
        )
        if stored is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado",
            )
        user = UserRepository.get_by_id(db, stored.user_id)
        if user is None or not user.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o desactivado",
            )
        # Rotación: revoca el actual y emite uno nuevo.
        RefreshTokenRepository.revoke(db, stored)
        return AuthService._issue_tokens(db, user)

    @staticmethod
    def logout(db: Session, raw_refresh: str | None = None, *, user: User | None = None) -> None:
        if raw_refresh:
            stored = RefreshTokenRepository.get_active_by_hash(
                db, hash_refresh_token(raw_refresh)
            )
            if stored is not None:
                RefreshTokenRepository.revoke(db, stored)
                db.commit()
            return
        if user is not None:
            RefreshTokenRepository.revoke_all_for_user(db, user.id)
            db.commit()
