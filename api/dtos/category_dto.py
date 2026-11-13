from pydantic import BaseModel, ConfigDict, Field

from api.dtos.product_dto import ProductRead


class CategoryBase(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    icon: str | None = Field(default=None, max_length=255)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=120)
    icon: str | None = Field(default=None, max_length=255)


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CategoryWithProducts(CategoryRead):
    products: list[ProductRead] = []
