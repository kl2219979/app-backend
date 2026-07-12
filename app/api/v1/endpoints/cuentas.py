from fastapi import APIRouter

router = APIRouter()


@router.get("/cuentas")
def cuentas_check() -> dict[str, str]:
    """ok si el servidor HTTP está arriba"""
    return {"status": "ok", "msg": "hola, hot-reload este el enpoint de las cuentas"}


@router.get("/cuentas/{cuenta_id}")
def get_cuenta(cuenta_id: int) -> dict[str, str]:
    """Obtiene una cuenta por su ID."""
    return {"status": "ok", "msg": f"cuenta {cuenta_id}"}


@router.post("/cuentas")
def create_cuenta() -> dict[str, str]:
    """Crea una nueva cuenta."""
    return {"status": "ok", "msg": "cuenta creada"}


@router.put("/cuentas/{cuenta_id}")
def update_cuenta(cuenta_id: int) -> dict[str, str]:
    """Actualiza una cuenta existente."""
    return {"status": "ok", "msg": f"cuenta {cuenta_id} actualizada"}


@router.delete("/cuentas/{cuenta_id}")
def delete_cuenta(cuenta_id: int) -> dict[str, str]:
    """Elimina una cuenta."""
    return {"status": "ok", "msg": f"cuenta {cuenta_id} eliminada"}