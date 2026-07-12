"""
Modelo User → tabla `users` en PostgreSQL.

CÓMO SE LEE ESTE ARCHIVO
------------------------
1. Importas tipos de columna (String, Date, ...).
2. Heredas de Base (así Alembic "ve" la tabla).
3. Defines __tablename__ (nombre real en la BD).
4. Cada atributo Mapped[...] = mapped_column(...) es una COLUMNA.

Luego:
  - Importar User en app/models/__init__.py
  - alembic revision --autogenerate -m "add users"
  - ./scripts/migrate.sh
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Un registro de la tabla users (una fila = una persona/cuenta)."""

    # Nombre de la tabla en Postgres (plural por convención).
    __tablename__ = "users"

    # --- Clave primaria ---
    # autoincrement: Postgres asigna 1, 2, 3... solo.
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # --- Datos personales ---
    # String(N) = VARCHAR(N). nullable=False = obligatorio.
    nombres: Mapped[str] = mapped_column(String(150), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    genero: Mapped[str] = mapped_column(String(30), nullable=False)

    # --- Cuenta / acceso ---
    # unique=True: no puede haber dos iguales en la tabla.
    # index=True: búsquedas más rápidas por ese campo (login, etc.).
    correo: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    usuario: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # NUNCA guardes la contraseña en texto plano.
    # Aquí guardas el HASH (lo calcularás luego en security.py / services).
    contrasena_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # --- Metadatos útiles ---
    # server_default=func.now(): la BD pone la fecha al insertar.
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
