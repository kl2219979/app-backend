from fastapi import APIRouter
from app.schemas.user import userCreate, userUpdate

router = APIRouter()


@router.get("/users")
def users_check() -> dict[str, str]:
    """ok si el servidor HTTP está arriba"""
    return {"status": "ok", "msg": "hola, hot-reload funcion userssss"}


@router.get("/users/{user_id}")
def get_user(user_id: int) -> dict[str, str]:
    """Obtener usuario por su ID"""
    return {"status": "ok", "msg": f"user {user_id}"}


@router.post("/users")
def create_user(data: userCreate) -> dict[str, str]:
    """Crea un nuevo usuario"""
    return {"status": "ok", "msg": "user creado"}


@router.put("/users/{user_id}")
def update_user(user_id: int, data: userUpdate) -> dict[str, str]:
    """Actualiza un usuario"""
    return {"status": "ok", "msg": f"user {user_id} actualizado"}


@router.delete("/users/{user_id}")
def delete_user(user_id: int) -> dict[str, str]:
    """Elimina un usuario"""
    return {"status": "ok", "msg": f"user {user_id} eliminado"}