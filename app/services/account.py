"""
app/services/account.py — Reglas de negocio de cuentas
======================================================

- El dueño de la cuenta es siempre el usuario del JWT (no confiar en user_id del body).
- Listar / obtener / actualizar / borrar solo sobre cuentas propias.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.user import User
from app.repositories.account import AccountRepository
from app.schemas.account import AccountCreate, AccountUpdate


class AccountService:
    @staticmethod
    def list_mine(db: Session, current_user: User) -> list[Account]:
        return AccountRepository.list_by_user(db, current_user.id)

    @staticmethod
    def get_mine(db: Session, current_user: User, account_id: int) -> Account:
        account = AccountRepository.get_by_id_for_user(
            db, account_id=account_id, user_id=current_user.id
        )
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada",
            )
        return account

    @staticmethod
    def create(db: Session, current_user: User, data: AccountCreate) -> Account:
        account = Account(
            user_id=current_user.id,
            banco=data.banco,
            tipo=data.tipo,
            moneda=data.moneda,
            saldo=data.saldo,
        )
        AccountRepository.create(db, account)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def update(
        db: Session,
        current_user: User,
        account_id: int,
        data: AccountUpdate,
    ) -> Account:
        account = AccountService.get_mine(db, current_user, account_id)
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(account, key, value)
        AccountRepository.update(db, account)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def delete(db: Session, current_user: User, account_id: int) -> None:
        account = AccountService.get_mine(db, current_user, account_id)
        AccountRepository.delete(db, account)
        db.commit()
