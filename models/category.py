from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.product import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    label: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)

    products: Mapped[list["Product"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )
