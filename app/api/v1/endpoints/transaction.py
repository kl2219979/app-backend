"""
app/api/v1/endpoints/transaction.py — CRUD de transacciones (JWT)
=================================================================

Rutas plurales: /transactions
Solo ves/editas movimientos de tus cuentas.

Listado paginado:
  GET /transactions?limit=20&offset=0
       &account_id=&category_id=&tipo=gasto|ingreso
       &date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
"""

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.pagination import Page
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.services.transaction import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=Page[TransactionResponse])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    account_id: int | None = Query(default=None, gt=0),
    category_id: int | None = Query(default=None, gt=0),
    tipo: Literal["gasto", "ingreso"] | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> Page[TransactionResponse]:
    return TransactionService.list_mine(
        db,
        current_user,
        account_id=account_id,
        category_id=category_id,
        tipo=tipo,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TransactionService.get_mine(db, current_user, transaction_id)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TransactionService.create(db, current_user, data)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TransactionService.update(db, current_user, transaction_id, data)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    TransactionService.delete(db, current_user, transaction_id)
