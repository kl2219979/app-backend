"""
app/repositories/account.py — Acceso a datos de Account
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.account import Account


class AccountRepository:
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
        return db.scalar(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id,
            )
        )

    @staticmethod
    def list_by_user(db: Session, user_id: int) -> list[Account]:
        items, _ = AccountRepository.list_filtered(
            db, user_id=user_id, limit=10_000, offset=0
        )
        return items

    @staticmethod
    def list_filtered(
        db: Session,
        *,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Account], int]:
        base = select(Account).where(Account.user_id == user_id)
        total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
        items = list(
            db.scalars(
                base.order_by(Account.id.desc()).limit(limit).offset(offset)
            ).all()
        )
        return items, int(total)

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
