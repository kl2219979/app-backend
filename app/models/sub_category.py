"""
Modelo SubCategory → tabla `sub_categories`.

Relaciones:
  SubCategory N ── 1 Category
  SubCategory 1 ── N Transaction

Ver mapa completo: docs/MODELOS.md
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.transaction import Transaction


class SubCategory(Base):
    """Subcategoría dentro de una categoría (ej. Supermercado bajo Alimentación)."""

    __tablename__ = "sub_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
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

    category: Mapped[Category] = relationship(back_populates="sub_categories")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="sub_category")

    def __repr__(self) -> str:
        return f"SubCategory(id={self.id}, nombre={self.nombre!r}, category_id={self.category_id})"
