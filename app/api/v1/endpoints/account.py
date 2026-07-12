from fastapi import APIRouter

router = APIRouter()


@router.get("/accounts")
def accounts_check() -> dict[str, str]:
    """ok si el servidor HTTP está arriba"""
    return {"status": "ok", "msg": "hola, hot-reload este el enpoint de las cuentas"}


@router.get("/accounts/{account_id}")
def get_account(account_id: int) -> dict[str, str]:
    """Obtiene una cuenta por su ID."""
    return {"status": "ok", "msg": f"account {account_id}"}


@router.post("/accounts")
def create_account() -> dict[str, str]:
    """Crea una nueva cuenta."""
    return {"status": "ok", "msg": "account creada"}


@router.put("/accounts/{account_id}")
def update_account(account_id: int) -> dict[str, str]:
    """Actualiza una cuenta existente."""
    return {"status": "ok", "msg": f"account {account_id} actualizada"}


@router.delete("/accounts/{account_id}")
def delete_account(account_id: int) -> dict[str, str]:
    """Elimina una cuenta."""
    return {"status": "ok", "msg": f"account {account_id} eliminada"}