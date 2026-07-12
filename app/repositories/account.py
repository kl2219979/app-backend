"""
app/repositories/account.py — Acceso a datos de Account
=======================================================

Cuentas bancarias / billeteras. Siempre filtrar por user_id en listados
del dueño (la regla de “solo mis cuentas” la aplica el service).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account


class AccountRepository:
    """CRUD de accounts."""

    @staticmethod
    def get_by_id(db: Session, account_id: int) -> Account | None:
        return db.get(Account, account_id)

    @staticmethod
    def get_by_id_for_user(
        db: Session,
        *,
        account_id: int,
        user_id: int,
    ) -> Account | None:
        """Cuenta por id solo si pertenece al user (evita fugas entre usuarios)."""
        return db.scalar(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id,
            )
        )

    @staticmethod
    def list_by_user(db: Session, user_id: int) -> list[Account]:
        """Todas las cuentas de un usuario, más recientes primero."""
        return list(
            db.scalars(
                select(Account)
                .where(Account.user_id == user_id)
                .order_by(Account.id.desc())
            ).all()
        )

    @staticmethod
    def create(db: Session, account: Account) -> Account:
        db.add(account)
        db.flush()
        db.refresh(account)
        return account

    @staticmethod
    def update(db: Session, account: Account) -> Account:
        db.add(account)
        db.flush()
        db.refresh(account)
        return account

    @staticmethod
    def delete(db: Session, account: Account) -> None:
        db.delete(account)
        db.flush()
