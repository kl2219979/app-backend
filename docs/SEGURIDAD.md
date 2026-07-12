# Autenticación y seguridad
# =========================
#
# Código
# ------
#   app/core/security.py     → hash bcrypt + JWT
#   app/api/deps.py          → get_db, get_current_user
#   app/api/v1/endpoints/auth.py → register / login / me
#   app/schemas/auth.py      → contratos JSON
#
# Principios
# ----------
# 1. Contraseña nunca en claro en BD (solo contrasena_hash).
# 2. Librerías estándar (bcrypt, PyJWT); no crypto casera.
# 3. SECRET_KEY y expiración salen de settings (.env).
# 4. Rutas protegidas usan Depends(get_current_user).
#
# Probar en Swagger (http://localhost:8000/docs)
# ----------------------------------------------
# 1. POST /api/v1/auth/register  (JSON con datos + contrasena)
# 2. POST /api/v1/auth/login     (form: username + password)
# 3. Botón Authorize → pegar el access_token
# 4. GET /api/v1/auth/me
#
# Proteger un endpoint nuevo
# --------------------------
#   from app.api.deps import get_current_user
#   from app.models.user import User
#
#   @router.get("/privado")
#   def privado(current_user: User = Depends(get_current_user)):
#       ...
#
# Mejoras a futuro
# ----------------
# - Refresh tokens
# - Roles / permisos (admin, user)
# - Rate limit en /login
# - Mover register/login a un UserService (capa services/)
# - Rotar SECRET_KEY y invalidar tokens
