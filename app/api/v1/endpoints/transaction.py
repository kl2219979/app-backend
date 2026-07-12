from fastapi import APIRouter

router = APIRouter()


@router.get("/transactions")
def transactions_check() -> dict[str, str]:
    """ok si el servidor HTTP está arriba"""
    return {"status": "ok", "msg": "hola, hot-reload este el enpoint de las TRANSACCIONESS ....."}


@router.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: int) -> dict[str, str]:
    """Obtiene transacción por su ID"""
    return {"status": "ok", "msg": f"transaction {transaction_id}"}


@router.post("/transactions")
def create_transaction() -> dict[str, str]:
    """Crea una nueva transacción"""
    return {"status": "ok", "msg": "transaction creada"}


@router.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int) -> dict[str, str]:
    """Actualiza una transacción existente"""
    return {"status": "ok", "msg": f"transaction {transaction_id} actualizada"}


@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int) -> dict[str, str]:
    """Elimina una transacción."""
    return {"status": "ok", "msg": f"transaction {transaction_id} eliminada"}