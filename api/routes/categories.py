from fastapi import APIRouter, Depends, status

from api.controllers.category_controller import CategoryController
from api.dtos.category_dto import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CategoryWithProducts,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(skip: int = 0, limit: int = 100, controller: CategoryController = Depends()):
    return controller.list_categories(skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: str, controller: CategoryController = Depends()):
    return controller.get_category(category_id)


@router.get("/{category_id}/products", response_model=CategoryWithProducts)
def get_category_products(category_id: str, controller: CategoryController = Depends()):
    return controller.get_category_with_products(category_id)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, controller: CategoryController = Depends()):
    return controller.create_category(data)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: str, data: CategoryUpdate, controller: CategoryController = Depends()):
    return controller.update_category(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, controller: CategoryController = Depends()):
    controller.delete_category(category_id)
