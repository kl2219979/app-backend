"""
app/schemas/auth.py — Contratos HTTP de autenticación
=====================================================

QUÉ ES
------
Schemas Pydantic para login / registro / respuesta de token.
Separados del modelo User para no exponer contrasena_hash.
"""

from datetime import date

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Body de registro: datos del usuario + contraseña en texto plano (solo en tránsito)."""

    nombres: str = Field(min_length=1, max_length=150)
    apellidos: str = Field(min_length=1, max_length=150)
    fecha_nacimiento: date
    genero: str = Field(min_length=1, max_length=30)
    correo: EmailStr
    usuario: str = Field(min_length=3, max_length=50)
    contrasena: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    """Lo que devolvemos al cliente (sin hash de contraseña)."""

    id: int
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    genero: str
    correo: EmailStr
    usuario: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Respuesta de login (OAuth2-compatible: access_token + token_type)."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Contenido útil del JWT tras decodificarlo (opcional / depuración)."""

    sub: str
