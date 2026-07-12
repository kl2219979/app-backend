"""
app/services/user.py — Reglas de negocio de usuarios
====================================================

El alta pública sigue en /auth/register.
Aquí: consultar y actualizar el propio perfil (o borrar la propia cuenta).
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    @staticmethod
    def get_by_id_for_viewer(db: Session, viewer: User, user_id: int) -> User:
        """Por ahora solo puedes ver tu propio usuario."""
        if viewer.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        user = UserRepository.get_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return user

    @staticmethod
    def update_me(db: Session, current_user: User, data: UserUpdate) -> User:
        payload = data.model_dump(exclude_unset=True)
        if "contrasena" in payload:
            plain = payload.pop("contrasena")
            current_user.contrasena_hash = hash_password(plain)

        if "correo" in payload:
            other = UserRepository.get_by_correo(db, payload["correo"])
            if other is not None and other.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Correo ya en uso",
                )
        if "usuario" in payload:
            other = UserRepository.get_by_usuario(db, payload["usuario"])
            if other is not None and other.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Usuario ya en uso",
                )

        for key, value in payload.items():
            setattr(current_user, key, value)
        UserRepository.update(db, current_user)
        db.commit()
        db.refresh(current_user)
        return current_user

    @staticmethod
    def delete_me(db: Session, current_user: User) -> None:
        UserRepository.delete(db, current_user)
        db.commit()
