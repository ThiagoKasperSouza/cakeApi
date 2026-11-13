from fastapi import Depends, HTTPException, status

from api.dtos.product_dto import ProductCreate, ProductUpdate
from models.product import Product
from services.category_service import CategoryService
from services.product_service import ProductService


class ProductController:
    def __init__(
        self,
        service: ProductService = Depends(),
        category_service: CategoryService = Depends(),
    ) -> None:
        self.service = service
        self.category_service = category_service

    def list_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: str | None = None,
    ) -> list[Product]:
        if category_id == "all":
            category_id = None
        return self.service.list_products(skip=skip, limit=limit, category_id=category_id)

    def get_product(self, product_id: int) -> Product:
        product = self.service.get_product(product_id)
        if product is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto não encontrado")
        return product

    def create_product(self, data: ProductCreate) -> Product:
        if data.category_id == "all":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "A opção Tudo não é uma categoria de produto")
        if self.category_service.get_category(data.category_id) is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Categoria não encontrada")
        return self.service.create_product(data)

    def update_product(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        if data.category_id == "all":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "A opção Tudo não é uma categoria de produto")
        if data.category_id is not None and self.category_service.get_category(data.category_id) is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Categoria não encontrada")
        return self.service.update_product(product, data)

    def delete_product(self, product_id: int) -> None:
        self.service.delete_product(self.get_product(product_id))
