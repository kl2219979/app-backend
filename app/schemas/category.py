from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class categoryCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = Field(max_length=255)


class categoryUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)


class categoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str
    creado_en: datetime
    actualizado_en: datetime