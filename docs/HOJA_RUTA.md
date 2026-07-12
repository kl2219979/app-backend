# Hoja de ruta — pasos 1 a 5 (implementados)
# ==========================================
#
# Este documento describe qué se hizo en cada paso de maduración del backend.
#
# ---------------------------------------------------------------------------
# Paso 1 — Unificar Alembic (un solo head)
# ---------------------------------------------------------------------------
# Problema: había varias revisiones vacías en paralelo → dos heads.
# Solución: se eliminaron las migraciones vacías:
#   - 08a8c3ba63f4_add_initial_schema.py
#   - c70ed89af933_add_initial_schema.py
#   - 72606699bc47_add_initial_schema.py
# Quedó solo: 72b0c849201b_add_initial_schema.py (DDL real).
#
# Si tu BD local tenía un revision_id borrado:
#   docker compose up db -d
#   alembic stamp 72b0c849201b
#   # o, si la BD está vacía:
#   ./scripts/migrate.sh
#
# Verificar:
#   alembic heads   → debe mostrar un solo head
#
# ---------------------------------------------------------------------------
# Paso 2 — CRUD real de Account (JWT + service + repository)
# ---------------------------------------------------------------------------
# Capas:
#   schemas/account.py     AccountCreate / Update / Response (sin user_id en create)
#   services/account.py    AccountService (solo cuentas del usuario del token)
#   endpoints/account.py   /api/v1/accounts  (Bearer obligatorio)
#   repositories/account.py (ya existía)
#
# Flujo: Endpoint → Service → Repository → Postgres
#
# ---------------------------------------------------------------------------
# Paso 3 — Tests AAA de auth + accounts
# ---------------------------------------------------------------------------
#   tests/conftest.py          SQLite en memoria + fixtures auth_headers
#   tests/api/test_auth.py     register / login / me
#   tests/api/test_accounts.py create / list / get / update / delete
#   tests/core/test_security.py (ya existía)
#
# Correr:  pytest -q
#
# ---------------------------------------------------------------------------
# Paso 4 — Category, SubCategory, Transaction
# ---------------------------------------------------------------------------
# Misma plantilla que Account:
#   services/category.py, sub_category.py, transaction.py
#   endpoints con rutas plurales y JWT
#
# Reglas extra en TransactionService:
#   - la cuenta debe ser del usuario
#   - subcategoría debe pertenecer a la categoría
#
# ---------------------------------------------------------------------------
# Paso 5 — Limpieza y unificación
# ---------------------------------------------------------------------------
# - Schemas en PascalCase (AccountCreate, …) con alias camelCase legacy
# - Rutas plurales:
#     /accounts  /categories  /subcategories  /transactions  /users
# - Stubs de hot-reload eliminados
# - Users: alta solo en /auth/register; /users/{id} es perfil propio
# - services/ poblado (ya no carpeta vacía)
#
# Mapa rápido de API (todas salvo health/auth-login/register requieren JWT
# excepto register/login/health):
#   POST /api/v1/auth/register
#   POST /api/v1/auth/login
#   GET  /api/v1/auth/me
#   CRUD /api/v1/accounts
#   CRUD /api/v1/categories
#   CRUD /api/v1/subcategories
#   CRUD /api/v1/transactions
#   GET/PUT/DELETE /api/v1/users/{id}  (solo el propio id)
#
# Ver también: docs/SEGURIDAD.md, docs/REPOSITORIOS.md, docs/TESTING.md
