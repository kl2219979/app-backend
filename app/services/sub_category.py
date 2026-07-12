"""
app/services/sub_category.py — Reglas de negocio de subcategorías
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.sub_category import SubCategory
from app.repositories.category import CategoryRepository
from app.repositories.sub_category import SubCategoryRepository
from app.schemas.sub_category import SubCategoryCreate, SubCategoryUpdate


class SubCategoryService:
    @staticmethod
    def list_all(db: Session, category_id: int | None = None) -> list[SubCategory]:
        if category_id is not None:
            if CategoryRepository.get_by_id(db, category_id) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada",
                )
            return SubCategoryRepository.list_by_category(db, category_id)
        return SubCategoryRepository.list_all(db)

    @staticmethod
    def get(db: Session, sub_category_id: int) -> SubCategory:
        item = SubCategoryRepository.get_by_id(db, sub_category_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subcategoría no encontrada",
            )
        return item

    @staticmethod
    def create(db: Session, data: SubCategoryCreate) -> SubCategory:
        if CategoryRepository.get_by_id(db, data.category_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
        item = SubCategory(
            category_id=data.category_id,
            nombre=data.nombre,
            descripcion=data.descripcion,
        )
        SubCategoryRepository.create(db, item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update(db: Session, sub_category_id: int, data: SubCategoryUpdate) -> SubCategory:
        item = SubCategoryService.get(db, sub_category_id)
        payload = data.model_dump(exclude_unset=True)
        if "category_id" in payload:
            if CategoryRepository.get_by_id(db, payload["category_id"]) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada",
                )
        for key, value in payload.items():
            setattr(item, key, value)
        SubCategoryRepository.update(db, item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, sub_category_id: int) -> None:
        item = SubCategoryService.get(db, sub_category_id)
        SubCategoryRepository.delete(db, item)
        db.commit()
