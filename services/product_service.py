from fastapi import Depends
from sqlalchemy.orm import Session

from api.dtos.product_dto import ProductCreate, ProductUpdate
from database.connection import get_db
from models.product import Product
from repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.repository = ProductRepository(db)

    def list_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
    ) -> list[Product]:
        return self.repository.list(skip=skip, limit=limit, category_id=category_id)

    def get_product(self, product_id: int) -> Product | None:
        return self.repository.get(product_id)

    def create_product(self, data: ProductCreate) -> Product:
        return self.repository.add(Product(**data.model_dump()))

    def update_product(self, product: Product, data: ProductUpdate) -> Product:
        return self.repository.update(product, data.model_dump(exclude_unset=True))

    def delete_product(self, product: Product) -> None:
        self.repository.delete(product)
