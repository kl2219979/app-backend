"""
app/services/transaction.py — Reglas de negocio de transacciones
================================================================

Validaciones clave:
- La cuenta debe pertenecer al usuario autenticado.
- La subcategoría debe pertenecer a la categoría indicada.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.account import AccountRepository
from app.repositories.category import CategoryRepository
from app.repositories.sub_category import SubCategoryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionService:
    @staticmethod
    def _ensure_category_pair(db: Session, category_id: int, sub_category_id: int) -> None:
        category = CategoryRepository.get_by_id(db, category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
        sub = SubCategoryRepository.get_by_id(db, sub_category_id)
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subcategoría no encontrada",
            )
        if sub.category_id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La subcategoría no pertenece a la categoría indicada",
            )

    @staticmethod
    def _ensure_own_account(db: Session, user: User, account_id: int) -> None:
        account = AccountRepository.get_by_id_for_user(
            db, account_id=account_id, user_id=user.id
        )
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada")

    @staticmethod
    def list_mine(db: Session, current_user: User) -> list[Transaction]:
        return TransactionRepository.list_by_user(db, current_user.id)

    @staticmethod
    def get_mine(db: Session, current_user: User, transaction_id: int) -> Transaction:
        item = TransactionRepository.get_by_id_for_user(
            db, transaction_id=transaction_id, user_id=current_user.id
        )
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada",
            )
        return item

    @staticmethod
    def create(db: Session, current_user: User, data: TransactionCreate) -> Transaction:
        TransactionService._ensure_own_account(db, current_user, data.account_id)
        TransactionService._ensure_category_pair(db, data.category_id, data.sub_category_id)
        item = Transaction(
            account_id=data.account_id,
            category_id=data.category_id,
            sub_category_id=data.sub_category_id,
            monto=data.monto,
            fecha=data.fecha,
            descripcion=data.descripcion,
        )
        TransactionRepository.create(db, item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update(
        db: Session,
        current_user: User,
        transaction_id: int,
        data: TransactionUpdate,
    ) -> Transaction:
        item = TransactionService.get_mine(db, current_user, transaction_id)
        payload = data.model_dump(exclude_unset=True)

        account_id = payload.get("account_id", item.account_id)
        category_id = payload.get("category_id", item.category_id)
        sub_category_id = payload.get("sub_category_id", item.sub_category_id)

        TransactionService._ensure_own_account(db, current_user, account_id)
        TransactionService._ensure_category_pair(db, category_id, sub_category_id)

        for key, value in payload.items():
            setattr(item, key, value)
        TransactionRepository.update(db, item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, current_user: User, transaction_id: int) -> None:
        item = TransactionService.get_mine(db, current_user, transaction_id)
        TransactionRepository.delete(db, item)
        db.commit()
