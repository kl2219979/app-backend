from fastapi import APIRouter

router = APIRouter()


@router.get("/transacciones")
def transacciones_check() -> dict[str, str]:
    """ok si el servidor HTTP está arriba"""
    return {"status": "ok", "msg": "hola, hot-reload este el enpoint de las TRANSACCIONESS ....."}


@router.get("/transacciones/{transaccion_id}")
def get_transaccion(transaccion_id: int) -> dict[str, str]:
    """Obtiene transacción por su ID"""
    return {"status": "ok", "msg": f"transaccion {transaccion_id}"}


@router.post("/transacciones")
def create_transaccion() -> dict[str, str]:
    """Crea una nueva transacción"""
    return {"status": "ok", "msg": "transaccion creada"}


@router.put("/transacciones/{transaccion_id}")
def update_transaccion(transaccion_id: int) -> dict[str, str]:
    """Actualiza una transacción existente"""
    return {"status": "ok", "msg": f"transaccion {transaccion_id} actualizada"}


@router.delete("/transacciones/{transaccion_id}")
def delete_transaccion(transaccion_id: int) -> dict[str, str]:
    """Elimina una transacción."""
    return {"status": "ok", "msg": f"transaccion {transaccion_id} eliminada"}