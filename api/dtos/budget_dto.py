from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.budget import BudgetStatus


class BudgetBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    customer: str = Field(min_length=1, max_length=150)
    description: str | None = None
    date: date_type
    amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    status: BudgetStatus = BudgetStatus.pending
    initials: str | None = Field(default=None, max_length=10)


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=50)
    customer: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    date: date_type | None = None
    amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    status: BudgetStatus | None = None
    initials: str | None = Field(default=None, max_length=10)


class BudgetRead(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
