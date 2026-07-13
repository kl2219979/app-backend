"""
app/services/report.py — Dashboard / estadísticas

Solo cuenta movimientos activos.
- gasto/ingreso = operativos
- transferencias se reportan aparte (no inflan gastos/ingresos del día a día)
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.account import AccountRepository
from app.schemas.report import (
    AccountSnapshot,
    CategoryBreakdown,
    MonthBucket,
    ReportSummary,
)


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

        filters = [
            Account.user_id == current_user.id,
            Transaction.activo.is_(True),
        ]
        if account_id is not None:
            filters.append(Transaction.account_id == account_id)
        if date_from is not None:
            filters.append(Transaction.fecha >= date_from)
        if date_to is not None:
            filters.append(Transaction.fecha <= date_to)

        by_tipo = (
            select(Transaction.tipo, func.coalesce(func.sum(Transaction.monto), 0))
            .join(Account, Transaction.account_id == Account.id)
            .where(*filters)
            .group_by(Transaction.tipo)
        )
        totals = {row[0]: Decimal(str(row[1])) for row in db.execute(by_tipo).all()}
        total_ingresos = totals.get("ingreso", Decimal("0"))
        total_gastos = totals.get("gasto", Decimal("0"))
        total_transferencias = totals.get("transferencia_salida", Decimal("0"))

        def _breakdown(tipo: str) -> list[CategoryBreakdown]:
            q = (
                select(
                    Category.id,
                    Category.nombre,
                    func.coalesce(func.sum(Transaction.monto), 0),
                )
                .join(Transaction, Transaction.category_id == Category.id)
                .join(Account, Transaction.account_id == Account.id)
                .where(*filters, Transaction.tipo == tipo)
                .group_by(Category.id, Category.nombre)
                .order_by(func.sum(Transaction.monto).desc())
            )
            return [
                CategoryBreakdown(
                    category_id=row[0],
                    nombre=row[1],
                    total=Decimal(str(row[2])),
                    tipo=tipo,
                )
                for row in db.execute(q).all()
            ]

        month_q = (
            select(
                extract("year", Transaction.fecha).label("y"),
                extract("month", Transaction.fecha).label("m"),
                Transaction.tipo,
                func.coalesce(func.sum(Transaction.monto), 0),
            )
            .join(Account, Transaction.account_id == Account.id)
            .where(*filters, Transaction.tipo.in_(("gasto", "ingreso")))
            .group_by("y", "m", Transaction.tipo)
            .order_by("y", "m")
        )
        month_map: dict[tuple[int, int], dict[str, Decimal]] = {}
        for row in db.execute(month_q).all():
            key = (int(row[0]), int(row[1]))
            month_map.setdefault(key, {"ingreso": Decimal("0"), "gasto": Decimal("0")})
            month_map[key][row[2]] = Decimal(str(row[3]))
        by_month = [
            MonthBucket(
                year=y,
                month=m,
                total_ingresos=vals.get("ingreso", Decimal("0")),
                total_gastos=vals.get("gasto", Decimal("0")),
                balance_neto=vals.get("ingreso", Decimal("0")) - vals.get("gasto", Decimal("0")),
            )
            for (y, m), vals in month_map.items()
        ]

        accounts = AccountRepository.list_filtered(
            db, user_id=current_user.id, only_active=False, limit=10_000, offset=0
        )[0]
        by_account: list[AccountSnapshot] = []
        for acc in accounts:
            if account_id is not None and acc.id != account_id:
                continue
            acc_filters = [
                Transaction.account_id == acc.id,
                Transaction.activo.is_(True),
                Transaction.tipo.in_(("gasto", "ingreso")),
            ]
            if date_from is not None:
                acc_filters.append(Transaction.fecha >= date_from)
            if date_to is not None:
                acc_filters.append(Transaction.fecha <= date_to)
            acc_q = (
                select(Transaction.tipo, func.coalesce(func.sum(Transaction.monto), 0))
                .where(*acc_filters)
                .group_by(Transaction.tipo)
            )
            acc_totals = {r[0]: Decimal(str(r[1])) for r in db.execute(acc_q).all()}
            by_account.append(
                AccountSnapshot(
                    account_id=acc.id,
                    banco=acc.banco,
                    moneda=acc.moneda,
                    saldo=Decimal(str(acc.saldo)),
                    activo=acc.activo,
                    total_ingresos=acc_totals.get("ingreso", Decimal("0")),
                    total_gastos=acc_totals.get("gasto", Decimal("0")),
                )
            )

        return ReportSummary(
            total_ingresos=total_ingresos,
            total_gastos=total_gastos,
            balance_neto=total_ingresos - total_gastos,
            total_transferencias=total_transferencias,
            by_category_gastos=_breakdown("gasto"),
            by_category_ingresos=_breakdown("ingreso"),
            by_month=by_month,
            by_account=by_account,
            date_from=date_from,
            date_to=date_to,
            account_id=account_id,
        )
