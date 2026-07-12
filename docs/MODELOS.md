# Mapa del modelo de datos (SQLAlchemy)
# =====================================
#
# Este documento explica las tablas, claves foráneas y cómo se relacionan.
# El código vive en `app/models/`. Alembic crea/actualiza el esquema en Postgres.
#
# Convención
# ----------
# - Archivo / clase: singular  →  user.py / User, account.py / Account
# - Tabla en Postgres: plural →  users, accounts, categories, ...
# - Dinero: Numeric(14, 2) / Decimal (no Float)
# - Fechas de auditoría: creado_en / actualizado_en con timezone
#
# Diagrama
# --------
#
#   users 1 ──────── N accounts 1 ──────── N transactions
#                                              │         │
#                                              │         │
#   categories 1 ──── N sub_categories ────────┘         │
#        │                                               │
#        └─────────────────── N transactions ────────────┘
#
#   (Transaction apunta a Account, Category y SubCategory)
#
# Tablas
# ------
#
# users
#   id (PK)
#   nombres, apellidos, fecha_nacimiento, genero
#   correo (unique), usuario (unique), contrasena_hash
#   creado_en
#
# accounts
#   id (PK)
#   user_id (FK → users.id)
#   banco, tipo, moneda, saldo
#   creado_en, actualizado_en
#
# categories
#   id (PK)
#   nombre (unique), descripcion
#   creado_en, actualizado_en
#
# sub_categories
#   id (PK)
#   category_id (FK → categories.id)
#   nombre, descripcion
#   creado_en, actualizado_en
#
# transactions
#   id (PK)
#   account_id      (FK → accounts.id)
#   category_id     (FK → categories.id)
#   sub_category_id (FK → sub_categories.id)
#   monto, fecha, descripcion
#   creado_en, actualizado_en
#
# Nota: category_id + sub_category_id
#   La subcategoría ya implica una categoría. Se guardan ambos para consultar
#   fácil; en el service valida que sub_category.category_id == category_id.
#
# Archivos
# --------
#   app/models/user.py
#   app/models/account.py
#   app/models/category.py
#   app/models/sub_category.py
#   app/models/transaction.py
#   app/models/__init__.py   ← importa todos (Alembic los detecta)
#
# Crear tablas en la BD
# ---------------------
#   docker compose up db -d
#   source .venv/bin/activate
#   alembic revision --autogenerate -m "add initial schema"
#   ./scripts/migrate.sh
#
# Revisar siempre el archivo generado en alembic/versions/ antes de aplicar.
