from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class subCategoryCreate(BaseModel):
    category_id: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = Field(max_length=255)


class subCategoryUpdate(BaseModel):
    category_id: int | None = Field(default=None, gt=0)
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)


class subCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    nombre: str
    descripcion: str
    creado_en: datetime
    actualizado_en: datetime