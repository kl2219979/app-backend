"""
Modelo User → tabla `users`.

Relaciones:
  User 1 ── N Account
  User 1 ── N RefreshToken

Ver mapa completo: docs/MODELOS.md
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.refresh_token import RefreshToken


class User(Base):
    """Persona/cuenta de acceso a la aplicación."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    nombres: Mapped[str] = mapped_column(String(150), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    genero: Mapped[str] = mapped_column(String(30), nullable=False)

    correo: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    usuario: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    contrasena_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # "user" | "admin" — admin puede mutar el catálogo de categorías.
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="user")

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    accounts: Mapped[list[Account]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def is_admin(self) -> bool:
        return self.rol == "admin"

    def __repr__(self) -> str:
        return f"User(id={self.id}, usuario={self.usuario!r}, rol={self.rol!r})"
