"""Schemas Pydantic del recurso Transaction."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    account_id: int = Field(gt=0)
    category_id: int = Field(gt=0)
    sub_category_id: int = Field(gt=0)
    monto: Decimal = Field(gt=0)
    fecha: date
    descripcion: str = Field(default="", max_length=255)


class TransactionUpdate(BaseModel):
    account_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    sub_category_id: int | None = Field(default=None, gt=0)
    monto: Decimal | None = Field(default=None, gt=0)
    fecha: date | None = None
    descripcion: str | None = Field(default=None, max_length=255)


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    category_id: int
    sub_category_id: int
    monto: Decimal
    fecha: date
    descripcion: str
    creado_en: datetime
    actualizado_en: datetime


transactionCreate = TransactionCreate
transactionUpdate = TransactionUpdate
transactionResponse = TransactionResponse
