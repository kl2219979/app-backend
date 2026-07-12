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
# Quien orquesta (service o endpoint) llama db.commit().
#
# Ejemplo
# -------
#   from app.repositories.account import AccountRepository
#   from app.models.account import Account
#
#   acc = Account(user_id=1, banco="X", tipo="ahorro", moneda="USD", saldo=0)
#   AccountRepository.create(db, acc)
#   db.commit()
#
# Métodos útiles por entidad
# --------------------------
# UserRepository
#   get_by_id, get_by_correo, get_by_usuario, get_by_correo_or_usuario
#   exists_correo_or_usuario, create, update, delete
#
# AccountRepository
#   get_by_id, get_by_id_for_user, list_by_user, create, update, delete
#
# CategoryRepository
#   get_by_id, get_by_nombre, list_all, create, update, delete
#
# SubCategoryRepository
#   get_by_id, list_by_category, list_all, create, update, delete
#
# TransactionRepository
#   get_by_id, get_by_id_for_user, list_by_account, list_by_user
#   create, update, delete
#
# Siguiente paso natural: services/ que usen estos repositories + reglas.
