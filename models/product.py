from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.category import Category


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    rating: Mapped[float | None] = mapped_column(Numeric(2, 1), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("categories.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    stock: Mapped[int] = mapped_column(default=0, nullable=False)

    category: Mapped["Category"] = relationship(back_populates="products")
