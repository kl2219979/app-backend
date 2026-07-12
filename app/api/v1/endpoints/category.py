from fastapi import APIRouter
from app.schemas.category import categoryCreate, categoryUpdate 


router = APIRouter()


@router.get("/category")
def category_check() -> dict[str, str]:
    """Responde ok si el servidor HTTP está arriba."""
    return {"status": "ok", "msg": "hola, hot-reload este el enpoint de las categoriass"}


@router.get("/category/{category_id}")
def get_category(category_id: int) -> dict[str, str]:
    """Obtiene una categoría por su ID."""
    return {"status": "ok", "msg": f"category {category_id}"}


@router.post("/category")
def create_category(data: categoryCreate) -> dict[str, str]:
    """Crea una nueva categoría."""
    return {"status": "ok", "msg": "categoria creada"}


@router.put("/category/{category_id}")
def update_category(category_id: int, data: categoryUpdate) -> dict[str, str]:
    """Actualiza una categoría existente."""
    return {"status": "ok", "msg": f"category {category_id} actualizada"}


@router.delete("/category/{category_id}")
def delete_category(category_id: int) -> dict[str, str]:
    """Elimina una categoría."""
    return {"status": "ok", "msg": f"category {category_id} eliminada"}
