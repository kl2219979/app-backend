"""Schemas de reportes / dashboard (solo movimientos activos)."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryBreakdown(BaseModel):
    category_id: int
    nombre: str
    total: Decimal
    tipo: str  # gasto | ingreso


class MonthBucket(BaseModel):
    year: int
    month: int
    total_ingresos: Decimal
    total_gastos: Decimal
    balance_neto: Decimal


class AccountSnapshot(BaseModel):
    account_id: int
    banco: str
    moneda: str
    saldo: Decimal
    activo: bool
    total_ingresos: Decimal
    total_gastos: Decimal


class ReportSummary(BaseModel):
    total_ingresos: Decimal = Field(ge=0)
    total_gastos: Decimal = Field(ge=0)
    balance_neto: Decimal
    total_transferencias: Decimal = Field(ge=0)
    by_category_gastos: list[CategoryBreakdown]
    by_category_ingresos: list[CategoryBreakdown]
    by_month: list[MonthBucket]
    by_account: list[AccountSnapshot]
    date_from: date | None = None
    date_to: date | None = None
    account_id: int | None = None
