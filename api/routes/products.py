from fastapi import APIRouter, Depends, status

from api.controllers.product_controller import ProductController
from api.dtos.product_dto import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(
    skip: int = 0,
    limit: int = 100,
    category_id: str | None = None,
    controller: ProductController = Depends(),
):
    return controller.list_products(skip=skip, limit=limit, category_id=category_id)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, controller: ProductController = Depends()):
    return controller.get_product(product_id)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, controller: ProductController = Depends()):
    return controller.create_product(data)


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, data: ProductUpdate, controller: ProductController = Depends()):
    return controller.update_product(product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, controller: ProductController = Depends()):
    controller.delete_product(product_id)
