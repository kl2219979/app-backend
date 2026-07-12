# Autenticación y seguridad
# =========================
#
# Código
# ------
#   app/core/security.py     → bcrypt + JWT access + hash de refresh
#   app/services/auth.py     → register / login / refresh / logout
#   app/api/deps.py          → get_db, get_current_user, get_current_admin
#   app/api/v1/endpoints/auth.py
#   app/models/refresh_token.py
#
# Tokens
# ------
# - access_token (JWT, tipicamente 30 min): header Authorization: Bearer
# - refresh_token (opaco, días): se guarda SOLO el hash en refresh_tokens
# - /auth/refresh rota el refresh (el anterior queda revocado)
# - /auth/logout revoca uno o todos los refresh del usuario
#
# Roles
# -----
# - users.rol: "user" (default) | "admin"
# - Admin puede mutar /categories y /subcategories
# - Promover: python scripts/promote_admin.py <usuario_o_correo>
#
# Flujo Swagger
# -------------
# 1. POST /auth/register
# 2. POST /auth/login → copiar access_token
# 3. Authorize → Bearer
# 4. GET /auth/me  (incluye rol)
#
# Variables
# ---------
#   SECRET_KEY
#   ACCESS_TOKEN_EXPIRE_MINUTES=30
#   REFRESH_TOKEN_EXPIRE_DAYS=14
#
