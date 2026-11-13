from datetime import date as date_type
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Period = Literal["day", "week", "month"]


class SeriesPoint(BaseModel):
    date: date_type
    label: str
    sales: float
    orders: int
    quotes: int


class TopPaidItem(BaseModel):
    id: int
    code: str
    customer: str
    amount: float
    date: date_type


class LowStockItem(BaseModel):
    id: int
    name: str
    category_id: str
    category_label: str
    stock: int


class MetricsWindow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: date_type = Field(serialization_alias="from")
    to: date_type


class MetricsOverview(BaseModel):
    period: Period
    window: MetricsWindow
    sales_total: float
    orders_count: int
    quotes_count: int
    average_ticket: float
    series: list[SeriesPoint]
    top_paid: list[TopPaidItem]
    low_stock: list[LowStockItem]
