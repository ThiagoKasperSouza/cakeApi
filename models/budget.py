import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class BudgetStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    paid = "paid"


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[BudgetStatus] = mapped_column(
        Enum(BudgetStatus, name="budget_status"),
        default=BudgetStatus.pending,
        nullable=False,
    )
    initials: Mapped[str | None] = mapped_column(String(10), nullable=True)
