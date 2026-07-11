"""
app/models/ — Tablas representadas en Python
--------------------------------------------

QUÉ ES
    Aquí defines las entidades (User, Product, etc.) como clases SQLAlchemy.

POR QUÉ EXISTE
    Es el puente entre "código" y "tablas".
    Alembic mira estos modelos para crear/alterar la BD desacoplada.

CÓMO AGREGAR UNA TABLA NUEVA
    1. Crea app/models/user.py con class User(Base): ...
    2. Impórtalo aquí:
           from app.models.user import User  # noqa: F401
    3. alembic revision --autogenerate -m "add users"
    4. ./scripts/migrate.sh

IMPORTANTE
    Definir el modelo NO inserta datos.
    Insertar/actualizar filas lo hacen services + repositories.
"""
