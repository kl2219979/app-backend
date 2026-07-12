"""
app/repositories/transaction.py — Acceso a datos de Transaction
===============================================================

Los filtros por dueño (user_id) se hacen vía Account.user_id (join),
porque Transaction no tiene user_id directo.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction


class TransactionRepository:
    """CRUD de transactions."""

    @staticmethod
    def get_by_id(db: Session, transaction_id: int) -> Transaction | None:
        return db.get(Transaction, transaction_id)

    @staticmethod
    def get_by_id_for_user(
        db: Session,
        *,
        transaction_id: int,
        user_id: int,
    ) -> Transaction | None:
        """Transacción solo si la cuenta asociada pertenece al user."""
        return db.scalar(
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(
                Transaction.id == transaction_id,
                Account.user_id == user_id,
            )
        )

    @staticmethod
    def list_by_account(db: Session, account_id: int) -> list[Transaction]:
        return list(
            db.scalars(
                select(Transaction)
                .where(Transaction.account_id == account_id)
                .order_by(Transaction.fecha.desc(), Transaction.id.desc())
            ).all()
        )

    @staticmethod
    def list_by_user(db: Session, user_id: int) -> list[Transaction]:
        """Todas las transacciones de todas las cuentas del usuario."""
        return list(
            db.scalars(
                select(Transaction)
                .join(Account, Transaction.account_id == Account.id)
                .where(Account.user_id == user_id)
                .order_by(Transaction.fecha.desc(), Transaction.id.desc())
            ).all()
        )

    @staticmethod
    def create(db: Session, transaction: Transaction) -> Transaction:
        db.add(transaction)
        db.flush()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def update(db: Session, transaction: Transaction) -> Transaction:
        db.add(transaction)
        db.flush()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def delete(db: Session, transaction: Transaction) -> None:
        db.delete(transaction)
        db.flush()
