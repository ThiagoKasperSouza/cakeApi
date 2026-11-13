from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dtos.category_dto import CategoryCreate, CategoryUpdate
from database.connection import get_db
from models.category import Category
from services.category_service import CategoryService


class CategoryController:
    def __init__(
        self,
        service: CategoryService = Depends(),
        db: Session = Depends(get_db),
    ) -> None:
        self.service = service
        self.db = db

    def list_categories(self, skip: int = 0, limit: int = 100) -> list[Category]:
        return self.service.list_categories(skip=skip, limit=limit)

    def get_category(self, category_id: int) -> Category:
        category = self.service.get_category(category_id)
        if category is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada")
        return category

    def get_category_with_products(self, category_id: int) -> Category:
        category = self.service.get_category_with_products(category_id)
        if category is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada")
        return category

    def create_category(self, data: CategoryCreate) -> Category:
        try:
            return self.service.create_category(data)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Categoria já existe") from None

    def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self.get_category(category_id)
        try:
            return self.service.update_category(category, data)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Categoria já existe") from None

    def delete_category(self, category_id: int) -> None:
        self.service.delete_category(self.get_category(category_id))
