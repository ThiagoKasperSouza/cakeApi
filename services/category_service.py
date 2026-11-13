from fastapi import Depends
from sqlalchemy.orm import Session

from api.dtos.category_dto import CategoryCreate, CategoryUpdate
from database.connection import get_db
from models.category import Category
from repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.repository = CategoryRepository(db)

    def list_categories(self, skip: int = 0, limit: int = 100) -> list[Category]:
        return self.repository.list(skip=skip, limit=limit)

    def get_category(self, category_id: str) -> Category | None:
        return self.repository.get(category_id)

    def get_category_with_products(self, category_id: str) -> Category | None:
        return self.repository.get_with_products(category_id)

    def create_category(self, data: CategoryCreate) -> Category:
        return self.repository.add(Category(**data.model_dump()))

    def update_category(self, category: Category, data: CategoryUpdate) -> Category:
        return self.repository.update(category, data.model_dump(exclude_unset=True))

    def delete_category(self, category: Category) -> None:
        self.repository.delete(category)
