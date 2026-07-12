"""
app/services/transaction.py — Reglas de negocio de transacciones
================================================================

Validaciones clave:
- La cuenta debe pertenecer al usuario autenticado.
- La subcategoría debe pertenecer a la categoría indicada.
- El saldo de la cuenta se actualiza según tipo:
    gasto   → resta monto
    ingreso → suma monto
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.account import AccountRepository
from app.repositories.category import CategoryRepository
from app.repositories.sub_category import SubCategoryRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.pagination import Page
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate


class TransactionService:
    @staticmethod
    def _delta(tipo: str, monto: Decimal) -> Decimal:
        """Impacto neto sobre el saldo de la cuenta."""
        if tipo == "ingreso":
            return monto
        if tipo == "gasto":
            return -monto
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tipo debe ser 'gasto' o 'ingreso'",
        )

    @staticmethod
    def _apply_saldo(account: Account, delta: Decimal) -> None:
        account.saldo = Decimal(account.saldo) + delta

    @staticmethod
    def _ensure_category_pair(db: Session, category_id: int, sub_category_id: int) -> None:
        category = CategoryRepository.get_by_id(db, category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
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
    def _get_own_account(db: Session, user: User, account_id: int) -> Account:
        account = AccountRepository.get_by_id_for_user(
            db, account_id=account_id, user_id=user.id
        )
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada",
            )
        return account

    @staticmethod
    def list_mine(
        db: Session,
        current_user: User,
        *,
        account_id: int | None = None,
        category_id: int | None = None,
        tipo: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Page[TransactionResponse]:
        if account_id is not None:
            TransactionService._get_own_account(db, current_user, account_id)
        items, total = TransactionRepository.list_filtered(
            db,
            user_id=current_user.id,
            account_id=account_id,
            category_id=category_id,
            tipo=tipo,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        return Page[TransactionResponse](
            items=[TransactionResponse.model_validate(i) for i in items],
            total=total,
            limit=limit,
            offset=offset,
        )

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
        account = TransactionService._get_own_account(db, current_user, data.account_id)
        TransactionService._ensure_category_pair(db, data.category_id, data.sub_category_id)
        item = Transaction(
            account_id=data.account_id,
            category_id=data.category_id,
            sub_category_id=data.sub_category_id,
            monto=data.monto,
            tipo=data.tipo,
            fecha=data.fecha,
            descripcion=data.descripcion,
        )
        TransactionRepository.create(db, item)
        TransactionService._apply_saldo(account, TransactionService._delta(item.tipo, item.monto))
        AccountRepository.update(db, account)
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
        new_tipo = payload.get("tipo", item.tipo)
        new_monto = payload.get("monto", item.monto)

        # Validar ANTES de tocar saldos (evita dejar la BD inconsistente).
        old_account = TransactionService._get_own_account(db, current_user, item.account_id)
        new_account = TransactionService._get_own_account(db, current_user, account_id)
        TransactionService._ensure_category_pair(db, category_id, sub_category_id)
        # Valida tipo vía _delta
        _ = TransactionService._delta(new_tipo, new_monto)

        TransactionService._apply_saldo(
            old_account,
            -TransactionService._delta(item.tipo, item.monto),
        )

        for key, value in payload.items():
            setattr(item, key, value)
        TransactionRepository.update(db, item)

        TransactionService._apply_saldo(
            new_account,
            TransactionService._delta(item.tipo, item.monto),
        )
        AccountRepository.update(db, old_account)
        if new_account.id != old_account.id:
            AccountRepository.update(db, new_account)

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, current_user: User, transaction_id: int) -> None:
        item = TransactionService.get_mine(db, current_user, transaction_id)
        account = TransactionService._get_own_account(db, current_user, item.account_id)
        TransactionService._apply_saldo(
            account,
            -TransactionService._delta(item.tipo, item.monto),
        )
        AccountRepository.update(db, account)
        TransactionRepository.delete(db, item)
        db.commit()
