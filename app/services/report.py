"""
app/services/report.py — Agregados para dashboard
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.account import AccountRepository
from app.schemas.report import CategoryTotal, ReportSummary


class ReportService:
    @staticmethod
    def summary(
        db: Session,
        current_user: User,
        *,
        account_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> ReportSummary:
        if account_id is not None:
            account = AccountRepository.get_by_id_for_user(
                db, account_id=account_id, user_id=current_user.id
            )
            if account is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cuenta no encontrada",
                )

        filters = [Account.user_id == current_user.id]
        if account_id is not None:
            filters.append(Transaction.account_id == account_id)
        if date_from is not None:
            filters.append(Transaction.fecha >= date_from)
        if date_to is not None:
            filters.append(Transaction.fecha <= date_to)

        base = (
            select(Transaction.tipo, func.coalesce(func.sum(Transaction.monto), 0))
            .join(Account, Transaction.account_id == Account.id)
            .where(*filters)
            .group_by(Transaction.tipo)
        )
        totals = {row[0]: Decimal(str(row[1])) for row in db.execute(base).all()}
        total_ingresos = totals.get("ingreso", Decimal("0"))
        total_gastos = totals.get("gasto", Decimal("0"))

        by_cat_q = (
            select(
                Category.id,
                Category.nombre,
                func.coalesce(func.sum(Transaction.monto), 0),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .join(Account, Transaction.account_id == Account.id)
            .where(*filters)
            .group_by(Category.id, Category.nombre)
            .order_by(func.sum(Transaction.monto).desc())
        )
        by_category = [
            CategoryTotal(
                category_id=row[0],
                nombre=row[1],
                total=Decimal(str(row[2])),
            )
            for row in db.execute(by_cat_q).all()
        ]

        return ReportSummary(
            total_ingresos=total_ingresos,
            total_gastos=total_gastos,
            balance_neto=total_ingresos - total_gastos,
            by_category=by_category,
            date_from=date_from,
            date_to=date_to,
            account_id=account_id,
        )
