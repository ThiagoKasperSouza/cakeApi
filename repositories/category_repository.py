from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.category import Category
from repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    model = Category

    def get_with_products(self, category_id: str) -> Category | None:
        return self.db.scalar(
            select(Category)
            .options(selectinload(Category.products))
            .where(Category.id == category_id)
        )
