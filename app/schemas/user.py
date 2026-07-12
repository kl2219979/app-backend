"""
app/schemas/user.py — Contratos HTTP de User (CRUD / perfil).

El registro público sigue en app.schemas.auth.UserRegister.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Alta de usuario (también usable internamente; preferir /auth/register)."""

    nombres: str = Field(min_length=1, max_length=150)
    apellidos: str = Field(min_length=1, max_length=150)
    fecha_nacimiento: date
    genero: str = Field(min_length=1, max_length=30)
    correo: str = Field(min_length=1, max_length=255)
    usuario: str = Field(min_length=3, max_length=50)
    contrasena: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    nombres: str | None = Field(default=None, min_length=1, max_length=150)
    apellidos: str | None = Field(default=None, min_length=1, max_length=150)
    fecha_nacimiento: date | None = None
    genero: str | None = Field(default=None, min_length=1, max_length=30)
    correo: str | None = Field(default=None, min_length=1, max_length=255)
    usuario: str | None = Field(default=None, min_length=3, max_length=50)
    contrasena: str | None = Field(default=None, min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    genero: str
    correo: str
    usuario: str
    rol: str
    creado_en: datetime


userCreate = UserCreate
userUpdate = UserUpdate
userResponse = UserResponse
