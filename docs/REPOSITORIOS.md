# Repositories (acceso a datos)
# =============================
#
# Cada archivo en app/repositories/ encapsula el SQL/ORM de una entidad.
# No usan schemas Pydantic; solo models + Session.
#
#   Endpoint/Service  →  Repository  →  PostgreSQL
#
# Convención de commit
# --------------------
# Los repositories hacen add/delete + flush (para obtener ids).
# Quien orquesta (service) llama db.commit().
#
# Listados paginados
# ------------------
# Preferir list_filtered(...) → (items, total) en accounts, categories,
# subcategories y transactions. Los métodos list_by_* / list_all son
# atajos de conveniencia donde aún existen.
#
# Métodos por entidad
# -------------------
# UserRepository
#   get_by_id, get_by_correo, get_by_usuario, get_by_correo_or_usuario
#   exists_correo_or_usuario, create, update, delete
#
# RefreshTokenRepository
#   create, get_active_by_hash, revoke, revoke_all_for_user
#
# AccountRepository
#   get_by_id, get_by_id_for_user, list_by_user, list_filtered
#   create, update, delete
#
# CategoryRepository
#   get_by_id, get_by_nombre, list_all, list_filtered
#   create, update, delete
#
# SubCategoryRepository
#   get_by_id, list_by_category, list_filtered
#   create, update, delete
#
# TransactionRepository
#   get_by_id, get_by_id_for_user, list_by_account, list_by_user, list_filtered
#   create, update, delete
