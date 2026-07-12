"""Schemas Pydantic del recurso Transaction."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TransactionTipo = Literal["gasto", "ingreso"]


class TransactionCreate(BaseModel):
    account_id: int = Field(gt=0)
    category_id: int = Field(gt=0)
    sub_category_id: int = Field(gt=0)
    monto: Decimal = Field(gt=0)
    tipo: TransactionTipo = "gasto"
    fecha: date
    descripcion: str = Field(default="", max_length=255)


class TransactionUpdate(BaseModel):
    account_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    sub_category_id: int | None = Field(default=None, gt=0)
    monto: Decimal | None = Field(default=None, gt=0)
    tipo: TransactionTipo | None = None
    fecha: date | None = None
    descripcion: str | None = Field(default=None, max_length=255)


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    category_id: int
    sub_category_id: int
    monto: Decimal
    tipo: TransactionTipo
    fecha: date
    descripcion: str
    creado_en: datetime
    actualizado_en: datetime
