"""
app/services/category.py — Reglas de negocio de categorías
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.pagination import Page


class CategoryService:
    @staticmethod
    def list_all(
        db: Session,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> Page[CategoryResponse]:
        items, total = CategoryRepository.list_filtered(db, limit=limit, offset=offset)
        return Page[CategoryResponse](
            items=[CategoryResponse.model_validate(i) for i in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def get(db: Session, category_id: int) -> Category:
        category = CategoryRepository.get_by_id(db, category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
        return category

    @staticmethod
    def create(db: Session, data: CategoryCreate) -> Category:
        if CategoryRepository.get_by_nombre(db, data.nombre) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría con ese nombre",
            )
        category = Category(nombre=data.nombre, descripcion=data.descripcion)
        CategoryRepository.create(db, category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def update(db: Session, category_id: int, data: CategoryUpdate) -> Category:
        category = CategoryService.get(db, category_id)
        payload = data.model_dump(exclude_unset=True)
        if "nombre" in payload:
            other = CategoryRepository.get_by_nombre(db, payload["nombre"])
            if other is not None and other.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una categoría con ese nombre",
                )
        for key, value in payload.items():
            setattr(category, key, value)
        CategoryRepository.update(db, category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, category_id: int) -> None:
        category = CategoryService.get(db, category_id)
        CategoryRepository.delete(db, category)
        db.commit()
