from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class accountCreate(BaseModel):
    user_id: int = Field(gt=0)
    banco: str = Field(min_length=1, max_length=100)
    tipo: str = Field(min_length=1, max_length=100)
    moneda: str = Field(min_length=1, max_length=10)
    saldo: Decimal = Field(default=Decimal("0.00"), ge=0)


class accountUpdate(BaseModel):
    banco: str | None = Field(default=None, min_length=1, max_length=100)
    tipo: str | None = Field(default=None, min_length=1, max_length=100)
    moneda: str | None = Field(default=None, min_length=1, max_length=10)
    saldo: Decimal | None = Field(default=None, ge=0)


class accountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    banco: str
    tipo: str
    moneda: str
    saldo: Decimal
    creado_en: datetime
    actualizado_en: datetime