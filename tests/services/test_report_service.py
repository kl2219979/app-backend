"""
Unit tests — ReportService (agregados).
"""

from datetime import date
from decimal import Decimal

import pytest

from app.schemas.transaction import TransactionCreate, TransferCreate
from app.services.report import ReportService
from app.services.transaction import TransactionService
from tests.helpers import make_account, make_category, make_sub_category, make_user

pytestmark = pytest.mark.unit


def test_summary_separates_gastos_ingresos_and_ignores_transfers_in_totals(db_session):
    user = make_user(db_session)
    account = make_account(db_session, user, saldo=Decimal("1000"))
    other = make_account(db_session, user, banco="Otra", saldo=Decimal("100"))
    category = make_category(db_session)
    sub = make_sub_category(db_session, category)

    TransactionService.create(
        db_session,
        user,
        TransactionCreate(
            account_id=account.id,
            category_id=category.id,
            sub_category_id=sub.id,
            monto=Decimal("100"),
            tipo="ingreso",
            fecha=date(2026, 7, 1),
            descripcion="sueldo",
        ),
    )
    TransactionService.create(
        db_session,
        user,
        TransactionCreate(
            account_id=account.id,
            category_id=category.id,
            sub_category_id=sub.id,
            monto=Decimal("40"),
            tipo="gasto",
            fecha=date(2026, 7, 2),
            descripcion="compra",
        ),
    )
    TransactionService.transfer(
        db_session,
        user,
        TransferCreate(
            from_account_id=account.id,
            to_account_id=other.id,
            monto=Decimal("10"),
            fecha=date(2026, 7, 3),
            category_id=category.id,
            sub_category_id=sub.id,
        ),
    )

    summary = ReportService.summary(db_session, user)

    assert summary.total_ingresos == Decimal("100")
    assert summary.total_gastos == Decimal("40")
    assert summary.balance_neto == Decimal("60")
    assert summary.total_transferencias == Decimal("10")
    assert len(summary.by_category_gastos) == 1
    assert summary.by_category_gastos[0].total == Decimal("40")
    assert len(summary.by_category_ingresos) == 1
    assert summary.by_category_ingresos[0].total == Decimal("100")
    assert len(summary.by_month) >= 1
    assert len(summary.by_account) == 2
