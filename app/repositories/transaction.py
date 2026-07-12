"""
app/repositories/transaction.py — Acceso a datos de Transaction
===============================================================

Los filtros por dueño (user_id) se hacen vía Account.user_id (join),
porque Transaction no tiene user_id directo.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
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
        items, _ = TransactionRepository.list_filtered(
            db,
            user_id=user_id,
            limit=10_000,
            offset=0,
        )
        return items

    @staticmethod
    def list_filtered(
        db: Session,
        *,
        user_id: int,
        account_id: int | None = None,
        category_id: int | None = None,
        tipo: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Transaction], int]:
        """Lista paginada con filtros opcionales. Retorna (items, total)."""
        filters = [Account.user_id == user_id]
        if account_id is not None:
            filters.append(Transaction.account_id == account_id)
        if category_id is not None:
            filters.append(Transaction.category_id == category_id)
        if tipo is not None:
            filters.append(Transaction.tipo == tipo)
        if date_from is not None:
            filters.append(Transaction.fecha >= date_from)
        if date_to is not None:
            filters.append(Transaction.fecha <= date_to)

        base = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(*filters)
        )
        total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
        items = list(
            db.scalars(
                base.order_by(Transaction.fecha.desc(), Transaction.id.desc())
                .limit(limit)
                .offset(offset)
            ).all()
        )
        return items, int(total)

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
