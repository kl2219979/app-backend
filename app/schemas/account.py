"""
app/schemas/account.py — Contratos HTTP de Account
==================================================

AccountCreate NO incluye user_id: el dueño sale del JWT (seguridad).
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    banco: str = Field(min_length=1, max_length=100)
    tipo: str = Field(min_length=1, max_length=100)
    moneda: str = Field(min_length=1, max_length=10)
    saldo: Decimal = Field(default=Decimal("0.00"), ge=0)


class AccountUpdate(BaseModel):
    banco: str | None = Field(default=None, min_length=1, max_length=100)
    tipo: str | None = Field(default=None, min_length=1, max_length=100)
    moneda: str | None = Field(default=None, min_length=1, max_length=10)
    saldo: Decimal | None = Field(default=None, ge=0)


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    banco: str
    tipo: str
    moneda: str
    saldo: Decimal
    creado_en: datetime
    actualizado_en: datetime


# Alias por compatibilidad con imports antiguos (camelCase).
accountCreate = AccountCreate
accountUpdate = AccountUpdate
accountResponse = AccountResponse
