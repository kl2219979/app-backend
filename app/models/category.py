"""
Modelo Category → tabla `categories`.

Relaciones:
  Category 1 ── N SubCategory
  Category 1 ── N Transaction

Ver mapa completo: docs/MODELOS.md
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.sub_category import SubCategory
    from app.models.transaction import Transaction


class Category(Base):
    """Categoría de gasto/ingreso (ej. Alimentación, Transporte)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Lado "uno": una categoría tiene muchas subcategorías.
    sub_categories: Mapped[list[SubCategory]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list[Transaction]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"Category(id={self.id}, nombre={self.nombre!r})"
