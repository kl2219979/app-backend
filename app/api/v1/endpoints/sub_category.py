from fastapi import APIRouter

router = APIRouter()


@router.get("/subcategory")
def sub_category_check() -> dict[str, str]:
    """Responde ok si el servidor HTTP está arriba."""
    return {"status": "ok", "msg": "hola, hot-reload este el enpoint de las SUB CATEGORIAS"}


@router.get("/subcategory/{subcategory_id}")
def get_sub_category(subcategory_id: int) -> dict[str, str]:
    """Obtiene una subcategoría por su ID."""
    return {"status": "ok", "msg": f"subcategory {subcategory_id}"}


@router.post("/subcategory")
def create_sub_category() -> dict[str, str]:
    """Crea una nueva subcategoría."""
    return {"status": "ok", "msg": "subcategoria creada"}


@router.put("/subcategory/{subcategory_id}")
def update_sub_category(subcategory_id: int) -> dict[str, str]:
    """Actualiza una subcategoría existente."""
    return {"status": "ok", "msg": f"subcategory {subcategory_id} actualizada"}


@router.delete("/subcategory/{subcategory_id}")
def delete_sub_category(subcategory_id: int) -> dict[str, str]:
    """Elimina una subcategoría."""
    return {"status": "ok", "msg": f"subcategory {subcategory_id} eliminada"}