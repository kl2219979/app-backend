"""
app/repositories/ — Acceso a datos (patrón repositorio)
=======================================================

QUÉ ES
------
Capas que ejecutan SELECT / INSERT / UPDATE / DELETE con SQLAlchemy.
Hablan con **models**, no con schemas Pydantic.

ARCHIVOS
--------
  user.py          → UserRepository
  account.py       → AccountRepository
  category.py      → CategoryRepository
  sub_category.py  → SubCategoryRepository
  transaction.py   → TransactionRepository

REGLAS
------
1. Reciben siempre `db: Session` (viene de get_db / Depends).
2. No hacen `db.commit()`: el service o endpoint confirma la transacción.
   Sí pueden hacer `flush()` + `refresh()` para obtener el `id`.
3. No contienen reglas de negocio (permisos, “¿puede borrar?”).
4. No importan FastAPI ni schemas.

USO TÍPICO
----------
    from app.repositories.account import AccountRepository

    account = AccountRepository.get_by_id_for_user(db, account_id=1, user_id=5)
    AccountRepository.create(db, Account(...))
    db.commit()

SIGUIENTE CAPA
--------------
services/ → usa repositories + security + reglas.
endpoints/ → usa services (o repos temporalmente) + schemas.
"""

from app.repositories.account import AccountRepository
from app.repositories.category import CategoryRepository
from app.repositories.sub_category import SubCategoryRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository

__all__ = [
    "AccountRepository",
    "CategoryRepository",
    "SubCategoryRepository",
    "TransactionRepository",
    "UserRepository",
]
