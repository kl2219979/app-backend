# Mapa del modelo de datos (SQLAlchemy)
# =====================================
#
# Principios de producto (dinero + usuarios):
# - Soft-delete: campo `activo`. DELETE HTTP desactiva; no borra historial.
# - Sin cascade delete-orphan en cuentas/categorías → no se pierde el ledger.
# - Account.saldo solo cambia por movimientos (y saldo_inicial al abrir cuenta).
# - Transferencias = dos piernas (transferencia_salida / transferencia_entrada)
#   unidas por grupo_transferencia (UUID).
#
# Diagrama
# --------
#
#   users 1 ──────── N accounts 1 ──────── N transactions
#                                              │         │
#   categories 1 ──── N sub_categories ────────┘         │
#        │                                               │
#        └─────────────────── N transactions ────────────┘
#
# Tablas
# ------
#
# users
#   id, nombres, apellidos, fecha_nacimiento, genero
#   correo, usuario, contrasena_hash, rol, activo, creado_en
#
# refresh_tokens
#   id, user_id, token_hash, expires_at, creado_en, revoked_at
#
# accounts
#   id, user_id, banco, tipo, moneda, saldo, activo
#   creado_en, actualizado_en
#
# categories / sub_categories
#   … + activo (desactivar categoría desactiva subcategorías hijas)
#
# transactions
#   account_id, category_id, sub_category_id
#   monto, tipo (gasto|ingreso|transferencia_salida|transferencia_entrada)
#   fecha, descripcion, activo, grupo_transferencia
#   creado_en, actualizado_en
#
# Contabilidad
# -----------
#   gasto / transferencia_salida  → resta saldo
#   ingreso / transferencia_entrada → suma saldo
#   Desactivar movimiento → revierte impacto (transferencia: ambas piernas)
#   Reportes: gastos/ingresos operativos separados; transferencias aparte
#
# Seeds: python scripts/seed.py (incluye categoría Transferencias)
