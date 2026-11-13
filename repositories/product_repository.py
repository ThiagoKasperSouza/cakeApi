from sqlalchemy import select

from models.product import Product
from repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
    ) -> list[Product]:
        stmt = select(Product)
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        return list(self.db.scalars(stmt.offset(skip).limit(limit)).all())
