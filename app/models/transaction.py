"""
Modelo Transaction → tabla `transactions`.

Relaciones:
  Transaction N ── 1 Account
  Transaction N ── 1 Category
  Transaction N ── 1 SubCategory

Nota de diseño:
  Se guardan category_id y sub_category_id.
  En el service conviene validar que la subcategoría pertenezca a esa categoría.

Ver mapa completo: docs/MODELOS.md
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.category import Category
    from app.models.sub_category import SubCategory


class Transaction(Base):
    """Movimiento de dinero asociado a una cuenta y su categorización."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )
    sub_category_id: Mapped[int] = mapped_column(
        ForeignKey("sub_categories.id"),
        nullable=False,
        index=True,
    )

    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    # "gasto" resta del saldo; "ingreso" suma. Default gasto (tracker de gastos).
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="gasto")
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
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

    account: Mapped[Account] = relationship(back_populates="transactions")
    category: Mapped[Category] = relationship(back_populates="transactions")
    sub_category: Mapped[SubCategory] = relationship(back_populates="transactions")

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self.id}, account_id={self.account_id}, "
            f"monto={self.monto}, fecha={self.fecha})"
        )
