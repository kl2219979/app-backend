"""
app/api/v1/endpoints/sub_category.py — CRUD de subcategorías (JWT)
==================================================================

Rutas plurales: /subcategories
Query opcional: ?category_id=1 para filtrar.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.sub_category import SubCategoryCreate, SubCategoryResponse, SubCategoryUpdate
from app.services.sub_category import SubCategoryService

router = APIRouter(prefix="/subcategories", tags=["subcategories"])


@router.get("", response_model=list[SubCategoryResponse])
def list_subcategories(
    category_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    _ = current_user
    return SubCategoryService.list_all(db, category_id=category_id)


@router.get("/{subcategory_id}", response_model=SubCategoryResponse)
def get_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    return SubCategoryService.get(db, subcategory_id)


@router.post("", response_model=SubCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_subcategory(
    data: SubCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    return SubCategoryService.create(db, data)


@router.put("/{subcategory_id}", response_model=SubCategoryResponse)
def update_subcategory(
    subcategory_id: int,
    data: SubCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    return SubCategoryService.update(db, subcategory_id, data)


@router.delete("/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _ = current_user
    SubCategoryService.delete(db, subcategory_id)
