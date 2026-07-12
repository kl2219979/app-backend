"""Schemas de reportes / dashboard."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryTotal(BaseModel):
    category_id: int
    nombre: str
    total: Decimal


class ReportSummary(BaseModel):
    total_ingresos: Decimal = Field(ge=0)
    total_gastos: Decimal = Field(ge=0)
    balance_neto: Decimal
    by_category: list[CategoryTotal]
    date_from: date | None = None
    date_to: date | None = None
    account_id: int | None = None
