"""
Modelo Account → tabla `accounts` (cuentas bancarias / billeteras).

Relaciones:
  Account N ── 1 User          (cada cuenta pertenece a un usuario)
  Account 1 ── N Transaction   (una cuenta tiene muchas transacciones)

Ver mapa completo: docs/MODELOS.md
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.user import User


class Account(Base):
    """Cuenta financiera de un usuario (banco, tipo, moneda, saldo)."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # FK → users.id  (antes estaba mal escrito como usuer_id)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    banco: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    moneda: Mapped[str] = mapped_column(String(10), nullable=False)
    # Numeric evita errores de redondeo típicos de Float con dinero.
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))

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

    user: Mapped[User] = relationship(back_populates="accounts")
    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"Account(id={self.id}, banco={self.banco!r}, "
            f"tipo={self.tipo!r}, moneda={self.moneda!r}, saldo={self.saldo})"
        )
